# Main Flask application
from flask import Flask, render_template, request, jsonify
import logging
import os
from data_parser import get_cached_stories, refresh_story_cache
from translator import translator_service

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
        stories = get_cached_stories()
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
        stories = get_cached_stories()
        story = next((s for s in stories if s.id == story_id), None)
        
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
        stories = get_cached_stories()
        stories_data = [story.to_dict() for story in stories]
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
        stories = refresh_story_cache()
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
        stories = get_cached_stories()
        
        # Count already translated stories
        already_translated = sum(1 for story in stories if story.translated_title)
        
        if already_translated == len(stories):
            return jsonify({
                'success': True,
                'message': 'All stories already translated',
                'priority_count': len(stories),
                'background_count': 0,
                'total_stories': len(stories),
                'already_completed': True
            })
        
        # Start smart translation (now fully async for fast response)
        translator_service.translate_stories_smart(stories, priority_count=3)
        
        # Return immediately without waiting for translation to complete
        untranslated_count = len(stories) - already_translated
        priority_count = min(3, untranslated_count)
        remaining_count = max(0, untranslated_count - priority_count)
        
        logger.info(f"Translation initiated: {priority_count} priority, {remaining_count} background")
        return jsonify({
            'success': True,
            'message': f'Translation started',
            'priority_count': priority_count,
            'background_count': remaining_count,
            'total_stories': len(stories),
            'already_completed': False
        })
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
        stories = get_cached_stories()
        translated_count = sum(1 for story in stories if story.translated_title)
        
        return jsonify({
            'success': True,
            'translated_count': translated_count,
            'total_stories': len(stories),
            'progress': round((translated_count / len(stories)) * 100, 1) if stories else 0
        })
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
        stories = get_cached_stories()
        translations = {}
        
        for story in stories:
            if story.translated_title:
                translations[story.id] = {
                    'original_title': story.title,
                    'translated_title': story.translated_title
                }
        
        return jsonify({
            'success': True,
            'translations': translations,
            'count': len(translations)
        })
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

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'stories_loaded': len(get_cached_stories())
    })

if __name__ == '__main__':
    # Load stories on startup
    try:
        stories = get_cached_stories()
        logger.info(f"Application started with {len(stories)} stories loaded")
    except Exception as e:
        logger.error(f"Error loading stories on startup: {e}")
    
    # Run the app
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )