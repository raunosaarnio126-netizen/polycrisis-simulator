#!/usr/bin/env python3

import requests
import sys
import json

class URLPathTester:
    def __init__(self, base_url="https://crisis-monitor-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None

    def login(self):
        """Login with test credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        url = f"{self.api_url}/login"
        response = requests.post(url, json=login_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access_token')
            return True
        return False

    def test_url_paths(self):
        """Test both old and new URL paths"""
        scenario_id = "9796a80e-976e-463d-ba00-aeb899b76a7a"
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        print("🔍 Testing URL Path Fix...")
        print(f"   Scenario ID: {scenario_id}")
        
        # Test 1: Old URL path (without hyphen) - should return 404
        old_url = f"{self.api_url}/scenarios/{scenario_id}/gamebook"
        print(f"\n📍 Testing OLD URL (should fail): {old_url}")
        
        try:
            response = requests.post(old_url, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 404:
                print("✅ OLD URL correctly returns 404 (not found)")
            else:
                print(f"❌ OLD URL returned unexpected status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing old URL: {e}")
            return False
        
        # Test 2: New URL path (with hyphen) - should work
        new_url = f"{self.api_url}/scenarios/{scenario_id}/game-book"
        print(f"\n📍 Testing NEW URL (should work): {new_url}")
        
        try:
            response = requests.post(new_url, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ NEW URL works correctly")
                data = response.json()
                print(f"   Game Book ID: {data.get('id')}")
                print(f"   Content length: {len(data.get('game_book_content', ''))}")
            else:
                print(f"❌ NEW URL returned unexpected status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error testing new URL: {e}")
            return False
        
        # Test 3: GET endpoints
        print(f"\n📍 Testing GET endpoints...")
        
        # Old GET URL
        old_get_url = f"{self.api_url}/scenarios/{scenario_id}/gamebook"
        print(f"   Testing OLD GET URL: {old_get_url}")
        try:
            response = requests.get(old_get_url, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 404:
                print("✅ OLD GET URL correctly returns 404")
            else:
                print(f"❌ OLD GET URL returned unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing old GET URL: {e}")
        
        # New GET URL
        new_get_url = f"{self.api_url}/scenarios/{scenario_id}/game-book"
        print(f"   Testing NEW GET URL: {new_get_url}")
        try:
            response = requests.get(new_get_url, headers=headers, timeout=30)
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ NEW GET URL works correctly")
                data = response.json()
                print(f"   Retrieved Game Book ID: {data.get('id')}")
            else:
                print(f"❌ NEW GET URL returned unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing new GET URL: {e}")
        
        return True

def main():
    print("🚀 Testing Game Book URL Path Fix")
    print("=" * 50)
    
    tester = URLPathTester()
    
    print("🔐 Logging in...")
    if not tester.login():
        print("❌ Failed to login")
        return 1
    
    print("✅ Login successful")
    
    success = tester.test_url_paths()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ URL Path Fix verification completed successfully!")
        print("   - Old URLs (/gamebook) correctly return 404")
        print("   - New URLs (/game-book) work correctly")
        return 0
    else:
        print("❌ URL Path Fix verification failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())