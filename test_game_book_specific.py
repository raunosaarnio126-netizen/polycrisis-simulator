#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class GameBookTester:
    def __init__(self, base_url="https://crisis-monitor-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=120)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=120)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=120)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=120)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_specific_game_book_scenario(self):
        """Test Game Book functionality with specific scenario from review request"""
        # Test credentials from review request
        test_email = "test@example.com"
        test_password = "password123"
        scenario_id = "9796a80e-976e-463d-ba00-aeb899b76a7a"
        
        print(f"\n🎯 Testing Game Book with specific scenario from review request...")
        print(f"   Scenario ID: {scenario_id}")
        print(f"   Title: Finnish Economic Crisis Test")
        print(f"   User: {test_email}")
        
        # First login with test credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_success, login_response = self.run_test(
            "Login with Test Credentials",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if not login_success or 'access_token' not in login_response:
            print("❌ Failed to login with test credentials")
            return False
            
        # Update token for subsequent requests
        self.token = login_response['access_token']
        print(f"   Logged in successfully with test credentials")
        
        # Test 1: Generate Game Book for specific scenario
        generate_success, generate_response = self.run_test(
            "Generate Game Book for Finnish Economic Crisis",
            "POST",
            f"scenarios/{scenario_id}/game-book",
            200
        )
        
        if not generate_success:
            print("❌ Failed to generate Game Book")
            return False
            
        # Verify Game Book response structure
        required_fields = ['id', 'scenario_id', 'game_book_content', 'decision_points', 
                         'resource_requirements', 'timeline_phases', 'success_metrics', 'created_at']
        
        missing_fields = []
        for field in required_fields:
            if field not in generate_response:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields in Game Book response: {missing_fields}")
            return False
            
        print(f"✅ Game Book generated successfully")
        print(f"   Game Book ID: {generate_response.get('id')}")
        print(f"   Content length: {len(generate_response.get('game_book_content', ''))}")
        print(f"   Decision points: {len(generate_response.get('decision_points', []))}")
        print(f"   Resource requirements: {len(generate_response.get('resource_requirements', []))}")
        print(f"   Timeline phases: {len(generate_response.get('timeline_phases', []))}")
        print(f"   Success metrics: {len(generate_response.get('success_metrics', []))}")
        
        # Verify AI content generation
        game_content = generate_response.get('game_book_content', '')
        if len(game_content) < 100:
            print(f"⚠️ Game Book content seems too short: {len(game_content)} characters")
            return False
            
        # Test 2: Retrieve Game Book for specific scenario
        retrieve_success, retrieve_response = self.run_test(
            "Retrieve Game Book for Finnish Economic Crisis",
            "GET",
            f"scenarios/{scenario_id}/game-book",
            200
        )
        
        if not retrieve_success:
            print("❌ Failed to retrieve Game Book")
            return False
            
        # Verify retrieved Game Book matches generated one
        if retrieve_response.get('id') != generate_response.get('id'):
            print("❌ Retrieved Game Book ID doesn't match generated one")
            return False
            
        if retrieve_response.get('scenario_id') != scenario_id:
            print(f"❌ Retrieved Game Book scenario_id doesn't match expected: {retrieve_response.get('scenario_id')} vs {scenario_id}")
            return False
            
        print(f"✅ Game Book retrieved successfully")
        print(f"   Retrieved Game Book ID matches generated: {retrieve_response.get('id')}")
        print(f"   Content consistency verified")
        
        # Test 3: Verify authentication is required
        temp_token = self.token
        self.token = None
        
        auth_test_success, auth_test_response = self.run_test(
            "Test Authentication Required for Game Book",
            "POST",
            f"scenarios/{scenario_id}/game-book",
            401  # Should fail without authentication
        )
        
        self.token = temp_token  # Restore token
        
        if not auth_test_success:
            print("❌ Authentication test failed - endpoint should require authentication")
            return False
            
        print(f"✅ Authentication properly enforced")
        
        # Test 4: Test with invalid scenario ID
        invalid_scenario_id = "invalid-scenario-id-12345"
        invalid_success, invalid_response = self.run_test(
            "Test Game Book with Invalid Scenario ID",
            "POST",
            f"scenarios/{invalid_scenario_id}/game-book",
            404  # Should return 404 for non-existent scenario
        )
        
        if not invalid_success:
            print("❌ Invalid scenario ID test failed - should return 404")
            return False
            
        print(f"✅ Invalid scenario ID properly handled with 404")
        
        return True

def main():
    print("🚀 Starting Game Book Specific Test")
    print("=" * 50)
    
    tester = GameBookTester()
    
    success = tester.test_specific_game_book_scenario()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if success:
        print("✅ All Game Book tests passed!")
        return 0
    else:
        print("❌ Some Game Book tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())