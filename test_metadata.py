#!/usr/bin/env python3
# Test story metadata rendering

from app import app

def test_metadata():
    with app.test_client() as client:
        response = client.get('/')
        content = response.data.decode('utf-8')
        
        print("Testing story metadata rendering:")
        print("✓ Points found" if 'points' in content else "✗ Points missing")
        print("✓ Author found" if 'hnuser' in content else "✗ Author missing")
        print("✓ Time found" if 'ago' in content else "✗ Time missing")
        print("✓ Comments found" if 'comments' in content else "✗ Comments missing")
        print("✓ Domain found" if 'sitestr' in content else "✗ Domain missing")
        
        # Check for specific elements
        if 'class="score"' in content:
            print("✓ Score styling applied")
        if 'class="hnuser"' in content:
            print("✓ User styling applied")
        if 'class="age"' in content:
            print("✓ Age styling applied")
        if 'class="sitebit"' in content:
            print("✓ Domain styling applied")

if __name__ == '__main__':
    test_metadata()