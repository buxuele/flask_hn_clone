#!/usr/bin/env python3
# Test homepage rendering

from app import app

def test_homepage():
    with app.test_client() as client:
        response = client.get('/')
        print(f"Homepage status: {response.status_code}")
        print(f"Content length: {len(response.data)}")
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            if 'Hacker News' in content and 'Hungary' in content:
                print("✓ Homepage rendered successfully with stories")
            else:
                print("✗ Homepage missing expected content")
        else:
            print("✗ Homepage failed to load")

if __name__ == '__main__':
    test_homepage()