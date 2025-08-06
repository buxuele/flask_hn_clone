#!/usr/bin/env python3
# Test Flask app after refactoring

from app import app
import json

def test_flask_app():
    """Test Flask app with new backend API structure"""
    print("🚀 Testing Flask App with Backend API...")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test 1: Homepage
        print("\n1. Testing homepage (/)...")
        response = client.get('/')
        if response.status_code == 200:
            print(f"✓ Homepage loaded successfully (status: {response.status_code})")
            print(f"  Content length: {len(response.data)} bytes")
        else:
            print(f"✗ Homepage failed (status: {response.status_code})")
        
        # Test 2: Health check
        print("\n2. Testing health check (/health)...")
        response = client.get('/health')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ Health check passed (status: {response.status_code})")
            print(f"  Health data: {data}")
        else:
            print(f"✗ Health check failed (status: {response.status_code})")
        
        # Test 3: API stories
        print("\n3. Testing API stories (/api/stories)...")
        response = client.get('/api/stories')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ API stories successful (status: {response.status_code})")
            print(f"  Stories count: {data.get('count', 0)}")
            print(f"  Success: {data.get('success', False)}")
        else:
            print(f"✗ API stories failed (status: {response.status_code})")
        
        # Test 4: Translation status
        print("\n4. Testing translation status (/api/translation-status)...")
        response = client.get('/api/translation-status')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ Translation status successful (status: {response.status_code})")
            print(f"  Progress: {data.get('progress', 0)}%")
            print(f"  Translated: {data.get('translated_count', 0)}/{data.get('total_stories', 0)}")
        else:
            print(f"✗ Translation status failed (status: {response.status_code})")
        
        # Test 5: Get translations
        print("\n5. Testing get translations (/api/translations)...")
        response = client.get('/api/translations')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ Get translations successful (status: {response.status_code})")
            print(f"  Translations count: {data.get('count', 0)}")
        else:
            print(f"✗ Get translations failed (status: {response.status_code})")
        
        # Test 6: Start translation
        print("\n6. Testing start translation (/api/translate)...")
        response = client.get('/api/translate')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ Start translation successful (status: {response.status_code})")
            print(f"  Priority count: {data.get('priority_count', 0)}")
            print(f"  Background count: {data.get('background_count', 0)}")
            print(f"  Already completed: {data.get('already_completed', False)}")
        else:
            print(f"✗ Start translation failed (status: {response.status_code})")
    
    print("\n" + "=" * 50)
    print("🎉 Flask app testing completed!")

if __name__ == '__main__':
    test_flask_app()