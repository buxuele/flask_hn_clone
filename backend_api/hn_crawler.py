# Hacker News data crawler
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from .models import Story

logger = logging.getLogger(__name__)

class HackerNewsCrawler:
    """Hacker News API crawler for fetching latest stories"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HN-Clone-Crawler/1.0'
        })
    
    def get_top_stories(self, limit: int = 30) -> List[int]:
        """Get top story IDs from HN API"""
        try:
            url = f"{self.base_url}/topstories.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()
            logger.info(f"Retrieved {len(story_ids)} top story IDs")
            return story_ids[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching top stories: {e}")
            return []
    
    def get_new_stories(self, limit: int = 30) -> List[int]:
        """Get new story IDs from HN API"""
        try:
            url = f"{self.base_url}/newstories.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()
            logger.info(f"Retrieved {len(story_ids)} new story IDs")
            return story_ids[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching new stories: {e}")
            return []
    
    def get_story_details(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed story information by ID"""
        try:
            url = f"{self.base_url}/item/{story_id}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            story_data = response.json()
            if not story_data:
                return None
                
            # Only process stories (not jobs, polls, etc.)
            if story_data.get('type') != 'story':
                return None
                
            return story_data
            
        except Exception as e:
            logger.error(f"Error fetching story {story_id}: {e}")
            return None
    
    def convert_to_story_model(self, story_data: Dict[str, Any], rank: int = 0) -> Optional[Story]:
        """Convert HN API data to our Story model"""
        try:
            # Extract basic information
            story_id = str(story_data.get('id', ''))
            title = story_data.get('title', '').strip()
            url = story_data.get('url', '')
            author = story_data.get('by', '')
            points = story_data.get('score', 0)
            comment_count = len(story_data.get('kids', []))
            timestamp = story_data.get('time', 0)
            
            # Calculate time ago
            time_ago = self.calculate_time_ago(timestamp)
            
            # Extract domain from URL
            domain = self.extract_domain(url) if url else ''
            
            # Create Story object
            story = Story(
                id=story_id,
                rank=rank,
                title=title,
                url=url,
                domain=domain,
                points=points,
                author=author,
                time_ago=time_ago,
                comment_count=comment_count
            )
            
            return story
            
        except Exception as e:
            logger.error(f"Error converting story data: {e}")
            return None
    
    def calculate_time_ago(self, timestamp: int) -> str:
        """Calculate human-readable time ago from timestamp"""
        try:
            now = datetime.now()
            story_time = datetime.fromtimestamp(timestamp)
            diff = now - story_time
            
            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if days > 0:
                return f"{days} day{'s' if days > 1 else ''} ago"
            elif hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif minutes > 0:
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "just now"
                
        except Exception as e:
            logger.error(f"Error calculating time ago: {e}")
            return "unknown"
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {e}")
            return ""
    
    def crawl_stories(self, story_type: str = 'top', limit: int = 30, batch_size: int = 10) -> List[Story]:
        """
        Crawl stories from HN API
        
        Args:
            story_type: 'top' or 'new'
            limit: Number of stories to fetch
            batch_size: Number of stories to fetch in parallel
            
        Returns:
            List of Story objects
        """
        logger.info(f"Starting to crawl {limit} {story_type} stories...")
        
        # Get story IDs
        if story_type == 'new':
            story_ids = self.get_new_stories(limit)
        else:
            story_ids = self.get_top_stories(limit)
        
        if not story_ids:
            logger.error("No story IDs retrieved")
            return []
        
        stories = []
        
        # Process stories in batches to avoid overwhelming the API
        for i in range(0, len(story_ids), batch_size):
            batch_ids = story_ids[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: stories {i+1}-{min(i+batch_size, len(story_ids))}")
            
            for j, story_id in enumerate(batch_ids):
                try:
                    story_data = self.get_story_details(story_id)
                    if story_data:
                        rank = i + j + 1
                        story = self.convert_to_story_model(story_data, rank)
                        if story and story.validate():
                            stories.append(story)
                            logger.info(f"✓ Story {rank}: {story.title[:50]}...")
                        else:
                            logger.warning(f"✗ Invalid story data for ID {story_id}")
                    else:
                        logger.warning(f"✗ No data for story ID {story_id}")
                        
                    # Rate limiting - be nice to HN API
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error processing story {story_id}: {e}")
                    continue
            
            # Pause between batches
            if i + batch_size < len(story_ids):
                logger.info("Pausing between batches...")
                time.sleep(1)
        
        logger.info(f"Successfully crawled {len(stories)} stories")
        return stories
    
    def save_stories_to_json(self, stories: List[Story], filename: Optional[str] = None) -> str:
        """
        Save stories to JSON file with timestamp
        
        Args:
            stories: List of Story objects
            filename: Optional custom filename
            
        Returns:
            Filename of saved file
        """
        if not filename:
            # Generate filename with timestamp: YYYYMMDD-HHMMSS
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"hn_stories_{timestamp}.json"
        
        try:
            # Convert stories to dict format
            stories_data = {
                'metadata': {
                    'crawl_time': datetime.now().isoformat(),
                    'total_stories': len(stories),
                    'source': 'hacker-news.firebaseio.com'
                },
                'stories': [story.to_dict() for story in stories]
            }
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stories_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(stories)} stories to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving stories to JSON: {e}")
            raise
    
    def load_stories_from_json(self, filename: str) -> List[Story]:
        """Load stories from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stories = []
            for story_data in data.get('stories', []):
                try:
                    # Create Story object from dict
                    story = Story(
                        id=story_data['id'],
                        rank=story_data['rank'],
                        title=story_data['title'],
                        url=story_data['url'],
                        domain=story_data['domain'],
                        points=story_data['points'],
                        author=story_data['author'],
                        time_ago=story_data['time_ago'],
                        comment_count=story_data['comment_count']
                    )
                    
                    # Set translated title if available
                    if story_data.get('translated_title'):
                        story.set_translated_title(story_data['translated_title'])
                    
                    stories.append(story)
                    
                except Exception as e:
                    logger.error(f"Error loading story from JSON: {e}")
                    continue
            
            logger.info(f"Loaded {len(stories)} stories from {filename}")
            return stories
            
        except Exception as e:
            logger.error(f"Error loading stories from JSON file {filename}: {e}")
            return []

# Global crawler instance
hn_crawler = HackerNewsCrawler()