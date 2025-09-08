import requests
import sys
import json
from datetime import datetime

class PolycrisisAPITester:
    def __init__(self, base_url="https://polycrisis-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_scenario_id = None

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
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

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

    def test_user_registration(self):
        """Test user registration"""
        test_user_data = {
            "email": f"test_user_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Test Organization"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
            return True, test_user_data
        return False, {}

    def test_user_login(self, user_data):
        """Test user login"""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Login token: {self.token[:20]}...")
            return True
        return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
            return True
        return False

    def test_create_scenario(self):
        """Test creating a crisis scenario"""
        scenario_data = {
            "title": "Test Earthquake Scenario",
            "description": "A major earthquake hitting a metropolitan area with cascading effects on infrastructure and population.",
            "crisis_type": "natural_disaster",
            "severity_level": 8,
            "affected_regions": ["California", "San Francisco Bay Area"],
            "key_variables": ["Population density", "Infrastructure age", "Emergency response capacity"]
        }
        
        success, response = self.run_test(
            "Create Scenario",
            "POST",
            "scenarios",
            200,
            data=scenario_data
        )
        
        if success and 'id' in response:
            self.created_scenario_id = response['id']
            print(f"   Created scenario ID: {self.created_scenario_id}")
            return True
        return False

    def test_get_scenarios(self):
        """Test getting user scenarios"""
        success, response = self.run_test(
            "Get Scenarios",
            "GET",
            "scenarios",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} scenarios")
            return True
        return False

    def test_get_single_scenario(self):
        """Test getting a single scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Single Scenario",
            "GET",
            f"scenarios/{self.created_scenario_id}",
            200
        )
        
        return success and 'id' in response

    def test_ai_genie(self):
        """Test AI Genie functionality"""
        ai_request = {
            "scenario_id": self.created_scenario_id,
            "user_query": "What are the key risks and mitigation strategies for this earthquake scenario?",
            "context": "Testing AI Genie functionality"
        }
        
        success, response = self.run_test(
            "AI Genie Chat",
            "POST",
            "ai-genie",
            200,
            data=ai_request
        )
        
        if success and 'response' in response:
            print(f"   AI Response length: {len(response.get('response', ''))}")
            print(f"   Suggestions count: {len(response.get('suggestions', []))}")
            print(f"   Monitoring tasks count: {len(response.get('monitoring_tasks', []))}")
            return True
        return False

    def test_run_simulation(self):
        """Test running simulation on scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for simulation")
            return False
            
        success, response = self.run_test(
            "Run Simulation",
            "POST",
            f"scenarios/{self.created_scenario_id}/simulate",
            200
        )
        
        if success and 'analysis' in response:
            print(f"   Analysis length: {len(response.get('analysis', ''))}")
            print(f"   Confidence score: {response.get('confidence_score', 'N/A')}")
            return True
        return False

    def test_delete_scenario(self):
        """Test deleting a scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for deletion")
            return False
            
        success, response = self.run_test(
            "Delete Scenario",
            "DELETE",
            f"scenarios/{self.created_scenario_id}",
            200
        )
        
        if success:
            print(f"   Scenario deleted successfully")
            # Verify scenario is actually deleted by trying to get it
            verify_success, verify_response = self.run_test(
                "Verify Scenario Deletion",
                "GET",
                f"scenarios/{self.created_scenario_id}",
                404
            )
            return verify_success
        return False

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            print(f"   Total scenarios: {response.get('total_scenarios', 'N/A')}")
            print(f"   Active scenarios: {response.get('active_scenarios', 'N/A')}")
            print(f"   Total simulations: {response.get('total_simulations', 'N/A')}")
            print(f"   Organization: {response.get('user_organization', 'N/A')}")
            return True
        return False

    def test_generate_game_book(self):
        """Test Game Book generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Game Book generation")
            return False
            
        success, response = self.run_test(
            "Generate Game Book",
            "POST",
            f"scenarios/{self.created_scenario_id}/game-book",
            200
        )
        
        if success and 'game_book_content' in response:
            print(f"   Game Book content length: {len(response.get('game_book_content', ''))}")
            print(f"   Decision points: {len(response.get('decision_points', []))}")
            print(f"   Resource requirements: {len(response.get('resource_requirements', []))}")
            print(f"   Timeline phases: {len(response.get('timeline_phases', []))}")
            print(f"   Success metrics: {len(response.get('success_metrics', []))}")
            return True
        return False

    def test_generate_action_plan(self):
        """Test Action Plan generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Action Plan generation")
            return False
            
        success, response = self.run_test(
            "Generate Action Plan",
            "POST",
            f"scenarios/{self.created_scenario_id}/action-plan",
            200
        )
        
        if success and 'immediate_actions' in response:
            print(f"   Immediate actions: {len(response.get('immediate_actions', []))}")
            print(f"   Short-term actions: {len(response.get('short_term_actions', []))}")
            print(f"   Long-term actions: {len(response.get('long_term_actions', []))}")
            print(f"   Responsible parties: {len(response.get('responsible_parties', []))}")
            print(f"   Priority level: {response.get('priority_level', 'N/A')}")
            return True
        return False

    def test_generate_strategy_implementation(self):
        """Test Strategy Implementation generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Strategy Implementation generation")
            return False
            
        success, response = self.run_test(
            "Generate Strategy Implementation",
            "POST",
            f"scenarios/{self.created_scenario_id}/strategy-implementation",
            200
        )
        
        if success and 'implementation_strategy' in response:
            print(f"   Implementation strategy length: {len(response.get('implementation_strategy', ''))}")
            print(f"   Organizational changes: {len(response.get('organizational_changes', []))}")
            print(f"   Policy recommendations: {len(response.get('policy_recommendations', []))}")
            print(f"   Training requirements: {len(response.get('training_requirements', []))}")
            print(f"   Budget considerations: {len(response.get('budget_considerations', []))}")
            print(f"   Stakeholder engagement: {len(response.get('stakeholder_engagement', []))}")
            return True
        return False

    def test_get_game_book(self):
        """Test retrieving Game Book"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Game Book retrieval")
            return False
            
        success, response = self.run_test(
            "Get Game Book",
            "GET",
            f"scenarios/{self.created_scenario_id}/game-book",
            200
        )
        
        return success and 'game_book_content' in response

    def test_get_action_plan(self):
        """Test retrieving Action Plan"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Action Plan retrieval")
            return False
            
        success, response = self.run_test(
            "Get Action Plan",
            "GET",
            f"scenarios/{self.created_scenario_id}/action-plan",
            200
        )
        
        return success and 'immediate_actions' in response

    def test_get_strategy_implementation(self):
        """Test retrieving Strategy Implementation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Strategy Implementation retrieval")
            return False
            
        success, response = self.run_test(
            "Get Strategy Implementation",
            "GET",
            f"scenarios/{self.created_scenario_id}/strategy-implementation",
            200
        )
        
        return success and 'implementation_strategy' in response

def main():
    print("🚀 Starting Polycrisis Simulator API Tests")
    print("=" * 50)
    
    tester = PolycrisisAPITester()
    
    # Test sequence
    print("\n📝 Testing Authentication Flow...")
    success, user_data = tester.test_user_registration()
    if not success:
        print("❌ Registration failed, stopping tests")
        return 1

    if not tester.test_user_login(user_data):
        print("❌ Login failed, stopping tests")
        return 1

    if not tester.test_get_user_profile():
        print("❌ Profile fetch failed, stopping tests")
        return 1

    print("\n🎯 Testing Scenario Management...")
    if not tester.test_create_scenario():
        print("❌ Scenario creation failed")
        
    tester.test_get_scenarios()
    tester.test_get_single_scenario()

    print("\n🤖 Testing AI Integration...")
    tester.test_ai_genie()
    tester.test_run_simulation()

    print("\n📊 Testing Dashboard...")
    tester.test_dashboard_stats()

    print("\n🗑️ Testing Scenario Deletion...")
    tester.test_delete_scenario()

    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())