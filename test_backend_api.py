#!/usr/bin/env python3
# Comprehensive test script for backend API service

from backend_api.api_service import api_service
from backend_api.translator import translator_service
import json
import time

def test_backend_api():
    """Test all backend API service functions"""
    print("🧪 Testing Backend API Service...")
    print("=" * 50)
    
    # Test 1: Get stories
    print("\n1. Testing get_stories()...")
    stories = api_service.get_stories()
    if stories:
        print(f"✓ Successfully loaded {len(stories)} stories")
        print(f"  First story: '{stories[0].title[:50]}...'")
        print(f"  Story ID: {stories[0].id}")
    else:
        print("✗ Failed to load stories")
        return
    
    # Test 2: Get stories as dict
    print("\n2. Testing get_stories_dict()...")
    stories_dict = api_service.get_stories_dict()
    if stories_dict:
        print(f"✓ Successfully converted {len(stories_dict)} stories to dict")
        print(f"  First story dict keys: {list(stories_dict[0].keys())}")
    else:
        print("✗ Failed to convert stories to dict")
    
    # Test 3: Get story by ID
    print("\n3. Testing get_story_by_id()...")
    if stories:
        test_story_id = stories[0].id
        story = api_service.get_story_by_id(test_story_id)
        if story:
            print(f"✓ Successfully found story by ID: {test_story_id}")
            print(f"  Story title: '{story.title[:50]}...'")
        else:
            print(f"✗ Failed to find story by ID: {test_story_id}")
    
    # Test 4: Health status
    print("\n4. Testing get_health_status()...")
    health = api_service.get_health_status()
    if health.get('status') == 'healthy':
        print("✓ Health check passed")
        print(f"  Status: {health}")
    else:
        print("✗ Health check failed")
        print(f"  Status: {health}")
    
    # Test 5: Translation status (before translation)
    print("\n5. Testing get_translation_status() (before translation)...")
    status = api_service.get_translation_status()
    if status.get('success'):
        print("✓ Translation status check successful")
        print(f"  Progress: {status.get('progress', 0)}%")
        print(f"  Translated: {status.get('translated_count', 0)}/{status.get('total_stories', 0)}")
    else:
        print("✗ Translation status check failed")
    
    # Test 6: Get translations (before translation)
    print("\n6. Testing get_translations() (before translation)...")
    translations = api_service.get_translations()
    if translations.get('success'):
        print("✓ Get translations successful")
        print(f"  Current translations count: {translations.get('count', 0)}")
    else:
        print("✗ Get translations failed")
    
    # Test 7: Start translation
    print("\n7. Testing translate_stories()...")
    translate_result = api_service.translate_stories(priority_count=2)
    if translate_result.get('success'):
        print("✓ Translation started successfully")
        print(f"  Priority count: {translate_result.get('priority_count', 0)}")
        print(f"  Background count: {translate_result.get('background_count', 0)}")
        print(f"  Already completed: {translate_result.get('already_completed', False)}")
        
        # Wait a bit for translation to start
        print("  Waiting 3 seconds for translation to process...")
        time.sleep(3)
        
        # Check translation progress
        print("\n8. Testing translation progress...")
        status = api_service.get_translation_status()
        if status.get('success'):
            print(f"✓ Translation progress: {status.get('progress', 0)}%")
            print(f"  Translated: {status.get('translated_count', 0)}/{status.get('total_stories', 0)}")
        
        # Check actual translations
        translations = api_service.get_translations()
        if translations.get('success') and translations.get('count', 0) > 0:
            print(f"✓ Found {translations.get('count', 0)} translations")
            # Show first translation
            first_translation = list(translations.get('translations', {}).values())[0]
            print(f"  Example: '{first_translation.get('original_title', '')[:30]}...'")
            print(f"       -> '{first_translation.get('translated_title', '')[:30]}...'")
    else:
        print("✗ Translation failed to start")
        print(f"  Error: {translate_result.get('error', 'Unknown error')}")
    
    # Test 8: Refresh stories
    print("\n9. Testing refresh_stories()...")
    refreshed_stories = api_service.refresh_stories()
    if refreshed_stories:
        print(f"✓ Successfully refreshed {len(refreshed_stories)} stories")
    else:
        print("✗ Failed to refresh stories")
    
    print("\n" + "=" * 50)
    print("🎉 Backend API testing completed!")

def test_translation_service():
    """Test translation service directly"""
    print("\n🌐 Testing Translation Service...")
    print("=" * 50)
    
    # Test simple translation
    test_text = "Hello, world!"
    translated = translator_service.translate_text(test_text)
    if translated and translated != test_text:
        print(f"✓ Translation test successful")
        print(f"  '{test_text}' -> '{translated}'")
    else:
        print(f"✗ Translation test failed or returned same text")
        print(f"  Input: '{test_text}', Output: '{translated}'")
    
    # Test cache
    cached_result = translator_service.translate_text(test_text)
    if cached_result == translated:
        print("✓ Translation cache working correctly")
    else:
        print("✗ Translation cache not working")

if __name__ == '__main__':
    test_backend_api()
    test_translation_service()