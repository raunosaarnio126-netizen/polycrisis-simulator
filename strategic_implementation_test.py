import requests
import sys
import json
import time
from datetime import datetime

class StrategyImplementationTester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_scenario_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test with configurable timeout"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            elapsed_time = time.time() - start_time
            print(f"   Status Code: {response.status_code} (took {elapsed_time:.2f}s)")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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

    def setup_test_user_and_scenario(self):
        """Setup test user and scenario for testing"""
        print("🔧 Setting up test user and scenario...")
        
        # Register user
        test_user_data = {
            "email": f"strategy_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"strategytest_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Strategy Test Organization"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "register",
            200,
            data=test_user_data,
            timeout=30
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
        else:
            return False
        
        # Create test scenario
        scenario_data = {
            "title": "Strategic Implementation Test Scenario",
            "description": "A comprehensive crisis scenario designed to test strategic implementation features including game book generation, action planning, and strategy implementation.",
            "crisis_type": "natural_disaster",
            "severity_level": 8,
            "affected_regions": ["California", "San Francisco Bay Area", "Silicon Valley"],
            "key_variables": ["Population density", "Infrastructure age", "Emergency response capacity", "Economic impact", "Supply chain disruption"]
        }
        
        success, response = self.run_test(
            "Create Test Scenario",
            "POST",
            "scenarios",
            200,
            data=scenario_data,
            timeout=30
        )
        
        if success and 'id' in response:
            self.created_scenario_id = response['id']
            print(f"   Created scenario ID: {self.created_scenario_id}")
            return True
        return False

    def test_game_book_generation(self):
        """Test Game Book generation with AI"""
        print("\n📖 Testing Game Book Generation...")
        
        success, response = self.run_test(
            "Generate Game Book",
            "POST",
            f"scenarios/{self.created_scenario_id}/game-book",
            200,
            timeout=120  # AI generation can take time
        )
        
        if success and 'game_book_content' in response:
            print(f"   ✅ Game Book generated successfully!")
            print(f"   📄 Content length: {len(response.get('game_book_content', ''))} characters")
            print(f"   🎯 Decision points: {len(response.get('decision_points', []))}")
            print(f"   🛠️  Resource requirements: {len(response.get('resource_requirements', []))}")
            print(f"   ⏱️  Timeline phases: {len(response.get('timeline_phases', []))}")
            print(f"   📊 Success metrics: {len(response.get('success_metrics', []))}")
            
            # Verify content quality
            content = response.get('game_book_content', '')
            if len(content) > 100:
                print(f"   ✅ Content appears substantial")
            else:
                print(f"   ⚠️  Content seems short")
                
            return True
        return False

    def test_action_plan_generation(self):
        """Test Action Plan generation with AI"""
        print("\n📋 Testing Action Plan Generation...")
        
        success, response = self.run_test(
            "Generate Action Plan",
            "POST",
            f"scenarios/{self.created_scenario_id}/action-plan",
            200,
            timeout=120  # AI generation can take time
        )
        
        if success and 'immediate_actions' in response:
            print(f"   ✅ Action Plan generated successfully!")
            print(f"   🚨 Immediate actions (0-24h): {len(response.get('immediate_actions', []))}")
            print(f"   📅 Short-term actions (1-30d): {len(response.get('short_term_actions', []))}")
            print(f"   📈 Long-term actions (1-12m): {len(response.get('long_term_actions', []))}")
            print(f"   👥 Responsible parties: {len(response.get('responsible_parties', []))}")
            print(f"   💰 Resource allocation items: {len(response.get('resource_allocation', []))}")
            print(f"   ⚡ Priority level: {response.get('priority_level', 'N/A')}")
            
            # Verify action categories have content
            immediate = response.get('immediate_actions', [])
            short_term = response.get('short_term_actions', [])
            long_term = response.get('long_term_actions', [])
            
            if len(immediate) >= 3 and len(short_term) >= 3 and len(long_term) >= 3:
                print(f"   ✅ All action categories have sufficient content")
            else:
                print(f"   ⚠️  Some action categories may be lacking content")
                
            return True
        return False

    def test_strategy_implementation_generation(self):
        """Test Strategy Implementation generation with AI"""
        print("\n🎯 Testing Strategy Implementation Generation...")
        
        success, response = self.run_test(
            "Generate Strategy Implementation",
            "POST",
            f"scenarios/{self.created_scenario_id}/strategy-implementation",
            200,
            timeout=120  # AI generation can take time
        )
        
        if success and 'implementation_strategy' in response:
            print(f"   ✅ Strategy Implementation generated successfully!")
            print(f"   📋 Implementation strategy length: {len(response.get('implementation_strategy', ''))} characters")
            print(f"   🏢 Organizational changes: {len(response.get('organizational_changes', []))}")
            print(f"   📜 Policy recommendations: {len(response.get('policy_recommendations', []))}")
            print(f"   🎓 Training requirements: {len(response.get('training_requirements', []))}")
            print(f"   💰 Budget considerations: {len(response.get('budget_considerations', []))}")
            print(f"   🤝 Stakeholder engagement: {len(response.get('stakeholder_engagement', []))}")
            
            # Verify content quality
            strategy = response.get('implementation_strategy', '')
            if len(strategy) > 200:
                print(f"   ✅ Strategy content appears comprehensive")
            else:
                print(f"   ⚠️  Strategy content seems brief")
                
            return True
        return False

    def test_retrieval_endpoints(self):
        """Test retrieval of generated implementation artifacts"""
        print("\n📥 Testing Retrieval of Generated Artifacts...")
        
        # Test Game Book retrieval
        success1, _ = self.run_test(
            "Retrieve Game Book",
            "GET",
            f"scenarios/{self.created_scenario_id}/game-book",
            200,
            timeout=30
        )
        
        # Test Action Plan retrieval
        success2, _ = self.run_test(
            "Retrieve Action Plan",
            "GET",
            f"scenarios/{self.created_scenario_id}/action-plan",
            200,
            timeout=30
        )
        
        # Test Strategy Implementation retrieval
        success3, _ = self.run_test(
            "Retrieve Strategy Implementation",
            "GET",
            f"scenarios/{self.created_scenario_id}/strategy-implementation",
            200,
            timeout=30
        )
        
        if success1 and success2 and success3:
            print("   ✅ All artifacts can be retrieved successfully!")
            return True
        else:
            print("   ⚠️  Some artifacts could not be retrieved")
            return False

    def test_data_persistence(self):
        """Test that generated data persists across requests"""
        print("\n💾 Testing Data Persistence...")
        
        # Generate new artifacts for the same scenario
        print("   Generating second set of artifacts...")
        
        success1, response1 = self.run_test(
            "Generate Second Game Book",
            "POST",
            f"scenarios/{self.created_scenario_id}/game-book",
            200,
            timeout=120
        )
        
        if success1:
            # Retrieve and verify it's the new one (should overwrite)
            success2, response2 = self.run_test(
                "Retrieve Updated Game Book",
                "GET",
                f"scenarios/{self.created_scenario_id}/game-book",
                200,
                timeout=30
            )
            
            if success2 and response1.get('id') == response2.get('id'):
                print("   ✅ Data persistence working correctly!")
                return True
            else:
                print("   ⚠️  Data persistence may have issues")
                return False
        return False

def main():
    print("🚀 Strategic Implementation Features Test")
    print("=" * 60)
    
    tester = StrategyImplementationTester()
    
    # Setup
    if not tester.setup_test_user_and_scenario():
        print("❌ Setup failed, cannot continue tests")
        return 1
    
    # Test all Strategic Implementation features
    tester.test_game_book_generation()
    tester.test_action_plan_generation()
    tester.test_strategy_implementation_generation()
    tester.test_retrieval_endpoints()
    tester.test_data_persistence()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Strategic Implementation tests passed!")
        return 0
    else:
        failed = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())