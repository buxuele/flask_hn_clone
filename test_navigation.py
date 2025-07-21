#!/usr/bin/env python3
# Test navigation routes

from app import app

def test_navigation():
    routes = ['/new', '/past', '/comments', '/ask', '/show', '/jobs', '/submit', '/login']
    
    with app.test_client() as client:
        print("Testing navigation routes:")
        for route in routes:
            response = client.get(route)
            print(f"✓ {route}: {response.status_code}")

if __name__ == '__main__':
    test_navigation()