#!/usr/bin/env python3
# Test script for HN crawler functionality

from backend_api.hn_crawler import hn_crawler
from backend_api.api_service import api_service
import json
import os
from datetime import datetime

def test_crawler():
    """Test the HN crawler functionality"""
    print("🕷️ Testing Hacker News Crawler...")
    print("=" * 60)
    
    # Test 1: Crawl top stories
    print("\n1. Testing crawl_stories() - Top Stories...")
    try:
        stories = hn_crawler.crawl_stories(story_type='top', limit=5)
        if stories:
            print(f"✓ Successfully crawled {len(stories)} top stories")
            for i, story in enumerate(stories[:3], 1):
                print(f"  {i}. [{story.rank}] {story.title[:50]}...")
                print(f"     Author: {story.author}, Points: {story.points}, Comments: {story.comment_count}")
                print(f"     Domain: {story.domain}, Time: {story.time_ago}")
        else:
            print("✗ Failed to crawl top stories")
            return
    except Exception as e:
        print(f"✗ Error crawling top stories: {e}")
        return
    
    # Test 2: Save to JSON
    print("\n2. Testing save_stories_to_json()...")
    try:
        filename = hn_crawler.save_stories_to_json(stories)
        print(f"✓ Successfully saved stories to {filename}")
        
        # Check if file exists and has content
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  File size: {os.path.getsize(filename)} bytes")
            print(f"  Stories in file: {len(data.get('stories', []))}")
            print(f"  Metadata: {data.get('metadata', {})}")
        else:
            print(f"✗ File {filename} was not created")
    except Exception as e:
        print(f"✗ Error saving to JSON: {e}")
        return
    
    # Test 3: Load from JSON
    print("\n3. Testing load_stories_from_json()...")
    try:
        loaded_stories = hn_crawler.load_stories_from_json(filename)
        if loaded_stories:
            print(f"✓ Successfully loaded {len(loaded_stories)} stories from JSON")
            print(f"  First story: {loaded_stories[0].title[:50]}...")
            print(f"  Last story: {loaded_stories[-1].title[:50]}...")
        else:
            print("✗ Failed to load stories from JSON")
    except Exception as e:
        print(f"✗ Error loading from JSON: {e}")
    
    # Test 4: Test new stories
    print("\n4. Testing crawl_stories() - New Stories...")
    try:
        new_stories = hn_crawler.crawl_stories(story_type='new', limit=3)
        if new_stories:
            print(f"✓ Successfully crawled {len(new_stories)} new stories")
            for i, story in enumerate(new_stories, 1):
                print(f"  {i}. [{story.rank}] {story.title[:50]}...")
        else:
            print("✗ Failed to crawl new stories")
    except Exception as e:
        print(f"✗ Error crawling new stories: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Crawler testing completed!")
    return filename

def test_api_service():
    """Test API service crawler functions"""
    print("\n🔧 Testing API Service Crawler Functions...")
    print("=" * 60)
    
    # Test 1: Crawl fresh stories via API service
    print("\n1. Testing api_service.crawl_fresh_stories()...")
    try:
        result = api_service.crawl_fresh_stories(story_type='top', limit=5)
        if result.get('success'):
            print(f"✓ API crawl successful")
            print(f"  Stories count: {result.get('stories_count', 0)}")
            print(f"  Filename: {result.get('filename', 'N/A')}")
            print(f"  Story type: {result.get('story_type', 'N/A')}")
            return result.get('filename')
        else:
            print(f"✗ API crawl failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error in API crawl: {e}")
        return None
    
    return None

def test_pagination():
    """Test pagination functionality"""
    print("\n📄 Testing Pagination Functionality...")
    print("=" * 60)
    
    # Test pagination with current stories
    print("\n1. Testing get_paginated_stories()...")
    try:
        # Test page 1
        result = api_service.get_paginated_stories(page=1, per_page=5)
        if result.get('success'):
            print(f"✓ Page 1 successful")
            pagination = result.get('pagination', {})
            print(f"  Stories on page: {len(result.get('stories', []))}")
            print(f"  Total stories: {pagination.get('total_stories', 0)}")
            print(f"  Total pages: {pagination.get('total_pages', 0)}")
            print(f"  Has next: {pagination.get('has_next', False)}")
            
            # Test page 2 if available
            if pagination.get('has_next'):
                result2 = api_service.get_paginated_stories(page=2, per_page=5)
                if result2.get('success'):
                    print(f"✓ Page 2 successful")
                    print(f"  Stories on page 2: {len(result2.get('stories', []))}")
        else:
            print(f"✗ Pagination failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error in pagination: {e}")

def test_flask_api():
    """Test Flask API endpoints"""
    print("\n🌐 Testing Flask API Endpoints...")
    print("=" * 60)
    
    from app import app
    
    with app.test_client() as client:
        # Test crawl endpoint
        print("\n1. Testing /api/crawl endpoint...")
        try:
            response = client.get('/api/crawl?type=top&limit=3')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✓ Crawl API successful (status: {response.status_code})")
                print(f"  Success: {data.get('success', False)}")
                print(f"  Stories count: {data.get('stories_count', 0)}")
                print(f"  Filename: {data.get('filename', 'N/A')}")
                
                # Test load JSON endpoint
                filename = data.get('filename')
                if filename:
                    print(f"\n2. Testing /api/load-json endpoint with {filename}...")
                    response2 = client.get(f'/api/load-json?filename={filename}')
                    if response2.status_code == 200:
                        data2 = json.loads(response2.data)
                        print(f"✓ Load JSON API successful (status: {response2.status_code})")
                        print(f"  Success: {data2.get('success', False)}")
                        print(f"  Stories count: {data2.get('stories_count', 0)}")
                    else:
                        print(f"✗ Load JSON API failed (status: {response2.status_code})")
            else:
                print(f"✗ Crawl API failed (status: {response.status_code})")
        except Exception as e:
            print(f"✗ Error testing Flask API: {e}")
        
        # Test pagination endpoint
        print(f"\n3. Testing /api/stories/paginated endpoint...")
        try:
            response = client.get('/api/stories/paginated?page=1&per_page=5')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✓ Pagination API successful (status: {response.status_code})")
                print(f"  Success: {data.get('success', False)}")
                print(f"  Stories on page: {len(data.get('stories', []))}")
                pagination = data.get('pagination', {})
                print(f"  Pagination info: Page {pagination.get('page', 0)}/{pagination.get('total_pages', 0)}")
            else:
                print(f"✗ Pagination API failed (status: {response.status_code})")
        except Exception as e:
            print(f"✗ Error testing pagination API: {e}")

if __name__ == '__main__':
    print("🚀 Starting Comprehensive Crawler Tests...")
    print("=" * 80)
    
    # Test crawler directly
    filename = test_crawler()
    
    # Test API service
    api_filename = test_api_service()
    
    # Test pagination
    test_pagination()
    
    # Test Flask API
    test_flask_api()
    
    print("\n" + "=" * 80)
    print("🎊 All crawler tests completed!")
    
    # Show created files
    print(f"\n📁 Files created during testing:")
    if filename:
        print(f"  - {filename}")
    if api_filename and api_filename != filename:
        print(f"  - {api_filename}")