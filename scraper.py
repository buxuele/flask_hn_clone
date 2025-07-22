import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_hacker_news_html():
    """Fetch the HTML content from the Hacker News homepage."""
    url = "https://news.ycombinator.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        logger.info(f"Successfully fetched HTML from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching HTML from {url}: {e}")
        return None
