# Backend API service - main business logic
import logging
from typing import List, Dict, Any, Optional
from .data_parser import get_cached_stories, refresh_story_cache
from .translator import translator_service
from .hn_crawler import hn_crawler
from .models import Story

logger = logging.getLogger(__name__)

class HackerNewsAPIService:
    """Main service class for Hacker News API operations"""
    
    def __init__(self):
        self.logger = logger
    
    def get_stories(self) -> List[Story]:
        """Get all stories from cache"""
        try:
            stories = get_cached_stories()
            self.logger.info(f"Retrieved {len(stories)} stories from cache")
            return stories
        except Exception as e:
            self.logger.error(f"Error getting stories: {e}")
            return []
    
    def get_stories_dict(self) -> List[Dict[str, Any]]:
        """Get all stories as dictionary list for JSON serialization"""
        try:
            stories = self.get_stories()
            return [story.to_dict() for story in stories]
        except Exception as e:
            self.logger.error(f"Error converting stories to dict: {e}")
            return []
    
    def refresh_stories(self) -> List[Story]:
        """Refresh story cache and return updated stories"""
        try:
            stories = refresh_story_cache()
            self.logger.info(f"Refreshed cache with {len(stories)} stories")
            return stories
        except Exception as e:
            self.logger.error(f"Error refreshing stories: {e}")
            return []
    
    def get_story_by_id(self, story_id: str) -> Optional[Story]:
        """Get a specific story by ID"""
        try:
            stories = self.get_stories()
            story = next((s for s in stories if s.id == story_id), None)
            if story:
                self.logger.info(f"Found story with ID: {story_id}")
            else:
                self.logger.warning(f"Story not found: {story_id}")
            return story
        except Exception as e:
            self.logger.error(f"Error getting story {story_id}: {e}")
            return None
    
    def translate_stories(self, priority_count: int = 3) -> Dict[str, Any]:
        """
        Translate stories with priority loading
        
        Args:
            priority_count: Number of priority stories to translate first
            
        Returns:
            Dictionary with translation status information
        """
        try:
            stories = self.get_stories()
            
            if not stories:
                return {
                    'success': False,
                    'error': 'No stories available for translation'
                }
            
            # Count already translated stories
            already_translated = sum(1 for story in stories if story.translated_title)
            
            if already_translated == len(stories):
                return {
                    'success': True,
                    'message': 'All stories already translated',
                    'priority_count': len(stories),
                    'background_count': 0,
                    'total_stories': len(stories),
                    'already_completed': True
                }
            
            # Start smart translation (fully async for fast response)
            translator_service.translate_stories_smart(stories, priority_count=priority_count)
            
            # Calculate counts
            untranslated_count = len(stories) - already_translated
            priority_count = min(priority_count, untranslated_count)
            remaining_count = max(0, untranslated_count - priority_count)
            
            self.logger.info(f"Translation initiated: {priority_count} priority, {remaining_count} background")
            
            return {
                'success': True,
                'message': 'Translation started',
                'priority_count': priority_count,
                'background_count': remaining_count,
                'total_stories': len(stories),
                'already_completed': False
            }
            
        except Exception as e:
            self.logger.error(f"Error in translation service: {e}")
            return {
                'success': False,
                'error': f'Translation failed: {str(e)}'
            }
    
    def get_translation_status(self) -> Dict[str, Any]:
        """Get current translation status"""
        try:
            stories = self.get_stories()
            if not stories:
                return {
                    'success': False,
                    'error': 'No stories available'
                }
            
            translated_count = sum(1 for story in stories if story.translated_title)
            progress = round((translated_count / len(stories)) * 100, 1) if stories else 0
            
            return {
                'success': True,
                'translated_count': translated_count,
                'total_stories': len(stories),
                'progress': progress
            }
            
        except Exception as e:
            self.logger.error(f"Error checking translation status: {e}")
            return {
                'success': False,
                'error': f'Failed to check translation status: {str(e)}'
            }
    
    def get_translations(self) -> Dict[str, Any]:
        """Get all current translations for dynamic update"""
        try:
            stories = self.get_stories()
            translations = {}
            
            for story in stories:
                if story.translated_title:
                    translations[story.id] = {
                        'original_title': story.title,
                        'translated_title': story.translated_title
                    }
            
            return {
                'success': True,
                'translations': translations,
                'count': len(translations)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting translations: {e}")
            return {
                'success': False,
                'error': f'Failed to get translations: {str(e)}'
            }
    
    def crawl_fresh_stories(self, story_type: str = 'top', limit: int = 30) -> Dict[str, Any]:
        """
        Crawl fresh stories from Hacker News API
        
        Args:
            story_type: 'top' or 'new'
            limit: Number of stories to crawl
            
        Returns:
            Dictionary with crawl results
        """
        try:
            self.logger.info(f"Starting to crawl {limit} {story_type} stories...")
            
            # Crawl stories from HN API
            stories = hn_crawler.crawl_stories(story_type=story_type, limit=limit)
            
            if not stories:
                return {
                    'success': False,
                    'error': 'No stories were crawled'
                }
            
            # Save to JSON file with timestamp
            filename = hn_crawler.save_stories_to_json(stories)
            
            return {
                'success': True,
                'message': f'Successfully crawled {len(stories)} {story_type} stories',
                'stories_count': len(stories),
                'filename': filename,
                'story_type': story_type
            }
            
        except Exception as e:
            self.logger.error(f"Error crawling stories: {e}")
            return {
                'success': False,
                'error': f'Crawling failed: {str(e)}'
            }
    
    def load_stories_from_json(self, filename: str) -> Dict[str, Any]:
        """
        Load stories from JSON file and update cache
        
        Args:
            filename: JSON filename to load from
            
        Returns:
            Dictionary with load results
        """
        try:
            stories = hn_crawler.load_stories_from_json(filename)
            
            if not stories:
                return {
                    'success': False,
                    'error': f'No stories loaded from {filename}'
                }
            
            # Update cache with loaded stories
            # Note: This is a simple approach, in production you might want more sophisticated caching
            get_cached_stories._cache = stories
            
            return {
                'success': True,
                'message': f'Successfully loaded {len(stories)} stories from {filename}',
                'stories_count': len(stories),
                'filename': filename
            }
            
        except Exception as e:
            self.logger.error(f"Error loading stories from JSON: {e}")
            return {
                'success': False,
                'error': f'Loading failed: {str(e)}'
            }
    
    def get_paginated_stories(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get paginated stories for infinite scroll
        
        Args:
            page: Page number (1-based)
            per_page: Number of stories per page
            
        Returns:
            Dictionary with paginated stories
        """
        try:
            stories = self.get_stories()
            
            if not stories:
                return {
                    'success': False,
                    'error': 'No stories available'
                }
            
            # Calculate pagination
            total_stories = len(stories)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            # Check if page is valid
            if start_idx >= total_stories:
                return {
                    'success': True,
                    'stories': [],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total_stories': total_stories,
                        'total_pages': (total_stories + per_page - 1) // per_page,
                        'has_next': False,
                        'has_prev': page > 1
                    }
                }
            
            # Get stories for current page
            page_stories = stories[start_idx:end_idx]
            total_pages = (total_stories + per_page - 1) // per_page
            
            return {
                'success': True,
                'stories': [story.to_dict() for story in page_stories],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_stories': total_stories,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1,
                    'start_idx': start_idx + 1,
                    'end_idx': min(end_idx, total_stories)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting paginated stories: {e}")
            return {
                'success': False,
                'error': f'Pagination failed: {str(e)}'
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get API health status"""
        try:
            stories = self.get_stories()
            return {
                'status': 'healthy',
                'stories_loaded': len(stories),
                'translation_service': 'active',
                'cache_status': 'active',
                'crawler_service': 'active'
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

# Global service instance
api_service = HackerNewsAPIService()