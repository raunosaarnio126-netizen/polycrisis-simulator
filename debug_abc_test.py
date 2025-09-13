import requests
import json

class DebugABCTester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None

    def login(self):
        """Login with test credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{self.api_url}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False

    def test_user_analytics(self):
        """Test user analytics endpoint"""
        headers = {'Authorization': f'Bearer {self.token}'}
        
        print("\n🔍 Testing user analytics endpoint...")
        response = requests.get(f"{self.api_url}/user/scenario-analytics", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User analytics working")
            print(json.dumps(data, indent=2))
            return True
        else:
            print("❌ User analytics failed")
            return False

    def test_get_scenarios(self):
        """Get all scenarios to understand sequence numbering"""
        headers = {'Authorization': f'Bearer {self.token}'}
        
        print("\n🔍 Getting all scenarios...")
        response = requests.get(f"{self.api_url}/scenarios", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            scenarios = response.json()
            print(f"Found {len(scenarios)} scenarios")
            
            for i, scenario in enumerate(scenarios):
                print(f"\nScenario {i+1}:")
                print(f"  ID: {scenario.get('id')}")
                print(f"  Title: {scenario.get('title')}")
                print(f"  Sequence Number: {scenario.get('sequence_number')}")
                print(f"  Sequence Letter: {scenario.get('sequence_letter')}")
                print(f"  Version: {scenario.get('version_number')}")
                print(f"  ABC Classification: {scenario.get('abc_classification')}")
                print(f"  Modification Count: {scenario.get('modification_count')}")
                print(f"  Revision Count: {scenario.get('revision_count')}")
            
            return True
        else:
            print("❌ Failed to get scenarios")
            return False

    def test_create_fresh_scenario(self):
        """Create a fresh scenario to test initial values"""
        headers = {'Authorization': f'Bearer {self.token}'}
        
        scenario_data = {
            "title": "Fresh Test Scenario",
            "description": "A completely new scenario to test initial tracking values",
            "crisis_type": "economic_crisis",
            "severity_level": 5,
            "affected_regions": ["Test Region"],
            "key_variables": ["Test Variable"]
        }
        
        print("\n🔍 Creating fresh scenario...")
        response = requests.post(f"{self.api_url}/scenarios", json=scenario_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            scenario = response.json()
            print("✅ Fresh scenario created")
            print(f"  ID: {scenario.get('id')}")
            print(f"  Title: {scenario.get('title')}")
            print(f"  Sequence Number: {scenario.get('sequence_number')}")
            print(f"  Sequence Letter: {scenario.get('sequence_letter')}")
            print(f"  Version: {scenario.get('version_number')}")
            print(f"  ABC Classification: {scenario.get('abc_classification')}")
            print(f"  Modification Count: {scenario.get('modification_count')}")
            print(f"  Revision Count: {scenario.get('revision_count')}")
            print(f"  Impact Score: {scenario.get('impact_score')}")
            print(f"  Economic Impact: {scenario.get('economic_impact')}")
            print(f"  Social Impact: {scenario.get('social_impact')}")
            print(f"  Environmental Impact: {scenario.get('environmental_impact')}")
            
            return scenario.get('id')
        else:
            print(f"❌ Failed to create scenario: {response.text}")
            return None

    def run_debug_tests(self):
        """Run debug tests"""
        print("="*60)
        print("DEBUG ABC TRACKING TESTS")
        print("="*60)
        
        if not self.login():
            return False
        
        # Test existing scenarios
        self.test_get_scenarios()
        
        # Test user analytics
        self.test_user_analytics()
        
        # Create fresh scenario
        fresh_id = self.test_create_fresh_scenario()
        
        # Test user analytics again after creating scenario
        if fresh_id:
            print("\n🔍 Testing user analytics after creating fresh scenario...")
            self.test_user_analytics()

if __name__ == "__main__":
    tester = DebugABCTester()
    tester.run_debug_tests()