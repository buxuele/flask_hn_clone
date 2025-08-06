# Translation service module
from deep_translator import GoogleTranslator
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional, List, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

class TranslationService:
    """Translation service using Google Translate API via deep-translator"""
    
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='zh-CN')
        self.cache = {}  # Simple in-memory cache
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum 100ms between requests
    
    def _rate_limit(self):
        """Simple rate limiting to avoid hitting API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def translate_text(self, text: str, target_lang: str = 'zh-CN', source_lang: str = 'auto') -> Optional[str]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code (default: 'zh-CN' for Simplified Chinese)
            source_lang: Source language code (default: 'auto' for auto-detection)
            
        Returns:
            Translated text or None if translation fails
        """
        if not text or not text.strip():
            return text
            
        # Create cache key
        cache_key = f"{text}:{source_lang}:{target_lang}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Rate limiting
            self._rate_limit()
            
            # Create translator with specific languages if different from default
            if target_lang != 'zh-CN' or source_lang != 'auto':
                translator = GoogleTranslator(source=source_lang, target=target_lang)
            else:
                translator = self.translator
            
            # Perform translation
            translated_text = translator.translate(text)
            
            # Cache the result
            self.cache[cache_key] = translated_text
            
            logger.info(f"Translated: '{text[:50]}...' -> '{translated_text[:50]}...'")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed for text '{text[:50]}...': {e}")
            return text  # Return original text if translation fails
    
    def translate_story_title(self, title: str) -> str:
        """Translate story title to Chinese"""
        return self.translate_text(title) or title
    
    def translate_batch_with_pause(self, texts: List[str], batch_size: int = 3, pause_seconds: float = 0.1) -> List[Tuple[int, str]]:
        """
        Translate multiple texts in batches with pauses to prevent overload
        
        Args:
            texts: List of texts to translate
            batch_size: Number of texts to translate in each batch
            pause_seconds: Seconds to pause between batches
            
        Returns:
            List of tuples (index, translated_text)
        """
        results = []
        
        # Process texts in batches
        for batch_start in range(0, len(texts), batch_size):
            batch_end = min(batch_start + batch_size, len(texts))
            batch_texts = texts[batch_start:batch_end]
            
            logger.info(f"Translating batch {batch_start//batch_size + 1}: items {batch_start+1}-{batch_end}")
            
            # Translate current batch
            for i, text in enumerate(batch_texts):
                actual_index = batch_start + i
                try:
                    translated_text = self.translate_text(text)
                    results.append((actual_index, translated_text))
                    logger.info(f"Batch progress: {actual_index+1}/{len(texts)} completed")
                except Exception as e:
                    logger.error(f"Translation failed for index {actual_index}: {e}")
                    results.append((actual_index, text))  # Return original text
            
            # Pause between batches (except for the last batch)
            if batch_end < len(texts):
                logger.info(f"Pausing {pause_seconds}s before next batch...")
                time.sleep(pause_seconds)
        
        # Sort results by index to maintain order
        results.sort(key=lambda x: x[0])
        return results
    
    def translate_stories_smart(self, stories, priority_count: int = 10):
        """
        Smart translation with priority and deduplication
        
        Args:
            stories: List of story objects
            priority_count: Number of priority stories to translate first
        """
        if not stories:
            return
        
        # Filter out already translated stories
        untranslated_stories = [story for story in stories if not story.translated_title]
        
        if not untranslated_stories:
            logger.info("All stories already translated")
            return
        
        # Split into priority and remaining
        priority_stories = untranslated_stories[:priority_count]
        remaining_stories = untranslated_stories[priority_count:]
        
        # Start priority translation in background thread for faster response
        if priority_stories:
            logger.info(f"Starting priority translation for {len(priority_stories)} stories")
            self._translate_priority_async(priority_stories)
        
        # Translate remaining stories in background
        if remaining_stories:
            logger.info(f"Starting background translation for {len(remaining_stories)} remaining stories")
            self._translate_background(remaining_stories)
    
    def _translate_priority_async(self, stories):
        """
        Translate priority stories asynchronously with immediate updates
        """
        def priority_translate():
            try:
                logger.info(f"Priority translation started for {len(stories)} stories")
                for i, story in enumerate(stories):
                    try:
                        # Create unique cache key using story ID
                        cache_key = f"{story.id}:{story.title}:zh-CN"
                        
                        if cache_key in self.cache:
                            translated_title = self.cache[cache_key]
                        else:
                            translated_title = self.translate_text(story.title)
                            self.cache[cache_key] = translated_title
                        
                        story.set_translated_title(translated_title)
                        logger.info(f"Priority {i+1}/{len(stories)}: '{story.title[:30]}...' -> '{translated_title[:30]}...'")
                        
                        # Add a small delay to allow for smoother updates
                        time.sleep(0.05)  # 50ms delay between priority translations
                        
                    except Exception as e:
                        logger.error(f"Failed to translate priority story {i+1}: {e}")
                
                logger.info(f"Priority translation completed for {len(stories)} stories")
            except Exception as e:
                logger.error(f"Priority translation failed: {e}")
        
        # Start priority translation thread
        thread = threading.Thread(target=priority_translate, daemon=True)
        thread.start()
        return thread
    
    def _translate_background(self, stories):
        """
        Translate stories in background thread with batch processing and pauses
        """
        def background_translate():
            try:
                logger.info(f"Starting background translation for {len(stories)} stories")
                titles = [story.title for story in stories]
                
                # Use batch translation with pauses
                results = self.translate_batch_with_pause(titles, batch_size=3, pause_seconds=0.1)
                
                # Update stories with translations
                for index, translated_title in results:
                    if index < len(stories):
                        # Create unique cache key
                        cache_key = f"{stories[index].id}:{stories[index].title}:zh-CN"
                        self.cache[cache_key] = translated_title
                        stories[index].set_translated_title(translated_title)
                
                logger.info(f"Background translation completed for {len(stories)} stories")
            except Exception as e:
                logger.error(f"Background translation failed: {e}")
        
        # Start background thread
        thread = threading.Thread(target=background_translate, daemon=True)
        thread.start()
        return thread
    
    def clear_cache(self):
        """Clear translation cache"""
        self.cache.clear()
        logger.info("Translation cache cleared")

# Global translator instance
translator_service = TranslationService()