# Data models and structures
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse
import re

@dataclass
class Story:
    """Data model for a Hacker News story"""
    id: str
    rank: int
    title: str
    url: str
    domain: str
    points: int
    author: str
    time_ago: str
    comment_count: int
    comment_text: str = field(init=False)  # Auto-generated from comment_count
    translated_title: Optional[str] = field(default=None, init=False)  # Translated title cache
    
    def __post_init__(self):
        """Set default values, validate data, and format comment text"""
        # Validate and clean data
        self.id = str(self.id).strip()
        self.rank = max(0, int(self.rank)) if self.rank is not None else 0
        self.title = str(self.title).strip()
        self.url = str(self.url).strip()
        self.points = max(0, int(self.points)) if self.points is not None else 0
        self.author = str(self.author).strip()
        self.time_ago = str(self.time_ago).strip()
        self.comment_count = max(0, int(self.comment_count)) if self.comment_count is not None else 0
        
        # Auto-extract domain if not provided
        if not self.domain and self.url:
            self.domain = self.extract_domain(self.url)
        
        # Format comment text
        self.comment_text = self.format_comment_text()
    
    def format_comment_text(self) -> str:
        """Format comment count into display text"""
        if self.comment_count == 0:
            return "discuss"
        elif self.comment_count == 1:
            return "1 comment"
        else:
            return f"{self.comment_count} comments"
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            # Handle URLs without protocol
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. prefix for cleaner display
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except Exception:
            return ""
    
    def is_external_link(self) -> bool:
        """Check if story links to external site"""
        return bool(self.url and not self.url.startswith('/'))
    
    def get_story_link(self) -> str:
        """Get the appropriate link for the story"""
        if self.is_external_link():
            return self.url
        else:
            return f"/item/{self.id}"
    
    def get_comment_link(self) -> str:
        """Get link to story comments"""
        return f"/item/{self.id}"
    
    def get_user_link(self) -> str:
        """Get link to user profile"""
        return f"/user/{self.author}"
    
    def get_display_title(self, use_translation: bool = False) -> str:
        """Get title for display, optionally translated"""
        if use_translation and self.translated_title:
            return self.translated_title
        return self.title
    
    def set_translated_title(self, translated_title: str):
        """Set the translated title"""
        self.translated_title = translated_title
    
    def validate(self) -> bool:
        """Validate story data integrity"""
        required_fields = [self.id, self.title, self.author]
        return all(field.strip() for field in required_fields)
    
    def to_dict(self) -> dict:
        """Convert story to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'rank': self.rank,
            'title': self.title,
            'url': self.url,
            'domain': self.domain,
            'points': self.points,
            'author': self.author,
            'time_ago': self.time_ago,
            'comment_count': self.comment_count,
            'comment_text': self.comment_text,
            'is_external': self.is_external_link(),
            'story_link': self.get_story_link(),
            'comment_link': self.get_comment_link(),
            'user_link': self.get_user_link()
        }