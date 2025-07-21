#!/usr/bin/env python3
# Simple test script for API endpoints

from app import app
import json

def test_api():
    with app.test_client() as client:
        # Test stories API
        response = client.get('/api/stories')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ API returned {data['count']} stories, success: {data['success']}")
        else:
            print(f"✗ API failed with status {response.status_code}")
        
        # Test health endpoint
        response = client.get('/health')
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✓ Health check: {data['status']}, stories loaded: {data['stories_loaded']}")
        else:
            print(f"✗ Health check failed with status {response.status_code}")

if __name__ == '__main__':
    test_api()