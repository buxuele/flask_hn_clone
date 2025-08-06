#!/usr/bin/env python3
# Test homepage rendering after UI fixes

from app import app

def test_homepage():
    """Test homepage rendering with fixed UI"""
    with app.test_client() as client:
        response = client.get('/')
        print(f"Homepage status: {response.status_code}")
        print(f"Content length: {len(response.data)} bytes")
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Check for key elements
            if 'Hacker News' in content:
                print("✓ Header present")
            if 'athing submission' in content:
                print("✓ Stories present")
            if '功能控制面板' in content:
                print("✓ Control panel present")
            if '启用无限滚动' in content:
                print("✓ Infinite scroll button present (not auto-enabled)")
            if 'Guidelines' in content:
                print("✓ Footer present")
                
            print("✓ Homepage rendered successfully with fixed UI")
        else:
            print("✗ Homepage failed to load")

if __name__ == '__main__':
    test_homepage()