# Main Flask application
from flask import Flask, render_template, request, jsonify
import logging
import os
from backend_api.api_service import api_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app with configuration
app = Flask(__name__)

# App configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
    DEBUG=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
    TEMPLATES_AUTO_RELOAD=True
)

@app.route('/')
def index():
    """Homepage with story list"""
    try:
        stories = api_service.get_stories()
        # Check if translation is requested
        translate = request.args.get('translate', 'false').lower() == 'true'
        logger.info(f"Serving homepage with {len(stories)} stories (translate: {translate})")
        return render_template('index.html', stories=stories, translate=translate)
    except Exception as e:
        logger.error(f"Error loading homepage: {e}")
        return render_template('error.html', 
                             error_message="Unable to load stories at this time."), 500

@app.route('/item/<story_id>')
def story(story_id):
    """Individual story page (placeholder)"""
    try:
        # Find the story by ID
        story = api_service.get_story_by_id(story_id)
        
        if story:
            logger.info(f"Serving story page for ID: {story_id}")
            return render_template('story.html', story=story)
        else:
            logger.warning(f"Story not found: {story_id}")
            return render_template('error.html', 
                                 error_message=f"Story {story_id} not found."), 404
    except Exception as e:
        logger.error(f"Error loading story {story_id}: {e}")
        return render_template('error.html', 
                             error_message="Unable to load story at this time."), 500

@app.route('/user/<username>')
def user(username):
    """User profile page (placeholder)"""
    try:
        logger.info(f"Serving user profile for: {username}")
        return render_template('user.html', username=username)
    except Exception as e:
        logger.error(f"Error loading user profile {username}: {e}")
        return render_template('error.html', 
                             error_message="Unable to load user profile at this time."), 500

# Navigation routes (placeholders)
@app.route('/new')
def new():
    """New stories page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="New Stories", 
                         message="New stories page coming soon!")

@app.route('/past')
def past():
    """Past stories page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Past Stories", 
                         message="Past stories page coming soon!")

@app.route('/comments')
def comments():
    """Comments page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Comments", 
                         message="Comments page coming soon!")

@app.route('/ask')
def ask():
    """Ask HN page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Ask HN", 
                         message="Ask HN page coming soon!")

@app.route('/show')
def show():
    """Show HN page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Show HN", 
                         message="Show HN page coming soon!")

@app.route('/jobs')
def jobs():
    """Jobs page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Jobs", 
                         message="Jobs page coming soon!")

@app.route('/submit')
def submit():
    """Submit page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Submit", 
                         message="Submit page coming soon!")

@app.route('/login')
def login():
    """Login page (placeholder)"""
    return render_template('placeholder.html', 
                         page_title="Login", 
                         message="Login page coming soon!")

# API routes
@app.route('/api/stories')
def api_stories():
    """API endpoint to get stories as JSON"""
    try:
        stories_data = api_service.get_stories_dict()
        return jsonify({
            'success': True,
            'count': len(stories_data),
            'stories': stories_data
        })
    except Exception as e:
        logger.error(f"Error in API stories endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to fetch stories'
        }), 500

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh story cache"""
    try:
        stories = api_service.refresh_stories()
        logger.info("Story cache refreshed via API")
        return jsonify({
            'success': True,
            'message': f'Cache refreshed with {len(stories)} stories'
        })
    except Exception as e:
        logger.error(f"Error refreshing cache via API: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to refresh cache'
        }), 500

@app.route('/api/translate')
def api_translate():
    """API endpoint to translate stories with priority loading"""
    try:
        result = api_service.translate_stories(priority_count=3)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in translation API: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to translate stories'
        }), 500

@app.route('/api/translation-status')
def api_translation_status():
    """API endpoint to check translation status"""
    try:
        result = api_service.get_translation_status()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error checking translation status: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to check translation status'
        }), 500

@app.route('/api/translations')
def api_translations():
    """API endpoint to get all translations for dynamic update"""
    try:
        result = api_service.get_translations()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting translations: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to get translations'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    return render_template('error.html', 
                         error_message="Page not found."), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return render_template('error.html', 
                         error_message="Internal server error."), 500

# Crawler API routes
@app.route('/api/crawl')
def api_crawl():
    """API endpoint to crawl fresh stories from HN"""
    try:
        story_type = request.args.get('type', 'top')  # 'top' or 'new'
        limit = int(request.args.get('limit', 30))
        
        result = api_service.crawl_fresh_stories(story_type=story_type, limit=limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in crawl API: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to crawl stories'
        }), 500

@app.route('/api/load-json')
def api_load_json():
    """API endpoint to load stories from JSON file"""
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename parameter is required'
            }), 400
        
        result = api_service.load_stories_from_json(filename)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in load JSON API: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to load stories from JSON'
        }), 500

@app.route('/api/stories/paginated')
def api_stories_paginated():
    """API endpoint to get paginated stories for infinite scroll"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        result = api_service.get_paginated_stories(page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in paginated stories API: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to get paginated stories'
        }), 500

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        result = api_service.get_health_status()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Load stories on startup
    try:
        stories = api_service.get_stories()
        logger.info(f"Application started with {len(stories)} stories loaded")
    except Exception as e:
        logger.error(f"Error loading stories on startup: {e}")
    
    # Run the app
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )