# HTML parsing and data extraction
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from models import Story
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_html_data(html_file_path="data.html"):
    """Parse the data.html file and extract story information"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        stories = []
        
        # Find all story rows - they have class "athing submission"
        story_rows = soup.find_all('tr', class_='athing submission')
        
        for story_row in story_rows:
            try:
                story = extract_story_info(story_row)
                if story and story.validate():
                    stories.append(story)
                else:
                    logger.warning(f"Invalid story data extracted: {story}")
            except Exception as e:
                logger.error(f"Error extracting story from row: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(stories)} stories from {html_file_path}")
        return stories
        
    except FileNotFoundError:
        logger.error(f"HTML file not found: {html_file_path}")
        return []
    except Exception as e:
        logger.error(f"Error parsing HTML file {html_file_path}: {e}")
        return []

def extract_story_info(story_row):
    """Extract individual story details from HTML element"""
    try:
        # Get story ID from the row id attribute
        story_id = story_row.get('id', '')
        
        # Get rank from the rank span
        rank_span = story_row.find('span', class_='rank')
        rank = 0
        if rank_span:
            rank_text = rank_span.get_text(strip=True).replace('.', '')
            rank = int(rank_text) if rank_text.isdigit() else 0
        
        # Get title and URL from the titleline span
        titleline = story_row.find('span', class_='titleline')
        if not titleline:
            return None
            
        title_link = titleline.find('a')
        if not title_link:
            return None
            
        title = title_link.get_text(strip=True)
        url = title_link.get('href', '')
        
        # Extract domain from sitebit if available
        domain = ""
        sitebit = titleline.find('span', class_='sitebit')
        if sitebit:
            sitestr = sitebit.find('span', class_='sitestr')
            if sitestr:
                domain = sitestr.get_text(strip=True)
        
        # If no domain found in sitebit, extract from URL
        if not domain and url:
            domain = extract_domain(url)
        
        # Find the next row which contains the subtext (points, author, time, comments)
        subtext_row = story_row.find_next_sibling('tr')
        if not subtext_row:
            return None
            
        subtext = subtext_row.find('td', class_='subtext')
        if not subtext:
            return None
        
        # Extract points
        points = 0
        score_span = subtext.find('span', class_='score')
        if score_span:
            score_text = score_span.get_text(strip=True)
            points_match = re.search(r'(\d+)', score_text)
            if points_match:
                points = int(points_match.group(1))
        
        # Extract author
        author = ""
        author_link = subtext.find('a', class_='hnuser')
        if author_link:
            author = author_link.get_text(strip=True)
        
        # Extract time ago
        time_ago = ""
        age_span = subtext.find('span', class_='age')
        if age_span:
            age_link = age_span.find('a')
            if age_link:
                time_ago = age_link.get_text(strip=True)
        
        # Extract comment count
        comment_count = 0
        comment_text = ""
        
        # Find comment link - it's usually the last link in subtext
        comment_links = subtext.find_all('a')
        for link in reversed(comment_links):
            link_text = link.get_text(strip=True)
            if 'comment' in link_text.lower() or link_text == 'discuss':
                comment_text = link_text
                # Extract number from comment text
                comment_match = re.search(r'(\d+)', link_text)
                if comment_match:
                    comment_count = int(comment_match.group(1))
                break
        
        # Create and return Story object
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
        logger.error(f"Error extracting story info: {e}")
        return None

def format_relative_time(time_string):
    """Convert timestamps to relative time format"""
    if not time_string:
        return ""
    
    # The time is already in relative format from HN (e.g., "5 hours ago")
    # Just clean it up if needed
    time_string = time_string.strip()
    
    # Handle various time formats
    if re.match(r'\d+\s+(hour|minute|day|week|month|year)s?\s+ago', time_string):
        return time_string
    
    # If it's just a number, assume it's hours
    if time_string.isdigit():
        hours = int(time_string)
        if hours == 1:
            return "1 hour ago"
        else:
            return f"{hours} hours ago"
    
    return time_string

def extract_domain(url):
    """Extract domain from URL"""
    if not url:
        return ""
    try:
        # Handle relative URLs
        if url.startswith('/'):
            return ""
        
        # Handle URLs without protocol
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix for cleaner display
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except Exception as e:
        logger.error(f"Error extracting domain from URL {url}: {e}")
        return ""

def get_cached_stories():
    """Get cached stories to avoid re-parsing on every request"""
    # Simple in-memory cache - in production, you might use Redis or similar
    if not hasattr(get_cached_stories, '_cache'):
        get_cached_stories._cache = parse_html_data()
    return get_cached_stories._cache

def refresh_story_cache():
    """Refresh the story cache"""
    if hasattr(get_cached_stories, '_cache'):
        delattr(get_cached_stories, '_cache')
    return get_cached_stories()