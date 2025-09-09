import requests
import sys
import json
from datetime import datetime

class FuzzyLogicTester:
    def __init__(self, base_url="https://crisis-adapt.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.company_id = None
        self.scenario_adjustment_id = None
        self.consensus_id = None
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
                response = requests.get(url, headers=test_headers, timeout=60)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=60)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=60)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=60)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
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

    def setup_test_environment(self):
        """Setup user, company for testing"""
        # Register user
        test_user_data = {
            "email": f"fuzzy_test_user_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"fuzzyuser_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Fuzzy Logic Test Org"
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
        else:
            return False

        # Get user profile
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
        else:
            return False

        # Create company
        company_data = {
            "company_name": "Fuzzy Logic Test Company",
            "industry": "Technology",
            "company_size": "medium",
            "website_url": "https://example.com",
            "description": "A test company for fuzzy logic scenario adjustments",
            "location": "San Francisco, CA"
        }
        
        success, response = self.run_test(
            "Create Company",
            "POST",
            "companies",
            200,
            data=company_data
        )
        
        if success and 'id' in response:
            self.company_id = response['id']
            print(f"   Company ID: {self.company_id}")
            return True
        else:
            return False

    def test_create_scenario_adjustment(self):
        """Test Creating Scenario Adjustment with SEPTE Framework"""
        adjustment_data = {
            "adjustment_name": "High Crisis Economic Scenario",
            "economic_crisis_pct": 60.0,
            "economic_stability_pct": 40.0,
            "social_unrest_pct": 30.0,
            "social_cohesion_pct": 70.0,
            "environmental_degradation_pct": 80.0,
            "environmental_resilience_pct": 20.0,
            "political_instability_pct": 45.0,
            "political_stability_pct": 55.0,
            "technological_disruption_pct": 25.0,
            "technological_advancement_pct": 75.0
        }
        
        success, response = self.run_test(
            "Create Scenario Adjustment",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            200,
            data=adjustment_data
        )
        
        if success and 'id' in response:
            self.scenario_adjustment_id = response['id']
            print(f"   ✅ Scenario adjustment created with ID: {self.scenario_adjustment_id}")
            print(f"   Adjustment name: {response.get('adjustment_name', 'N/A')}")
            print(f"   Real-time analysis length: {len(response.get('real_time_analysis', ''))}")
            print(f"   Risk level: {response.get('risk_level', 'N/A')}")
            
            # Verify SEPTE percentages
            septe_pairs = [
                ('economic_crisis_pct', 'economic_stability_pct'),
                ('social_unrest_pct', 'social_cohesion_pct'),
                ('environmental_degradation_pct', 'environmental_resilience_pct'),
                ('political_instability_pct', 'political_stability_pct'),
                ('technological_disruption_pct', 'technological_advancement_pct')
            ]
            
            for pair in septe_pairs:
                val1 = response.get(pair[0], 0)
                val2 = response.get(pair[1], 0)
                total = val1 + val2
                if abs(total - 100.0) > 0.1:
                    print(f"   ⚠️ SEPTE validation failed for {pair}: {val1} + {val2} = {total}")
                    return False
                else:
                    print(f"   ✅ SEPTE pair {pair[0]}/{pair[1]}: {val1}%/{val2}% = 100%")
            
            return True
        else:
            return False

    def test_percentage_validation(self):
        """Test SEPTE Percentage Validation"""
        invalid_adjustment_data = {
            "adjustment_name": "Invalid Percentage Test",
            "economic_crisis_pct": 60.0,
            "economic_stability_pct": 30.0,  # 60 + 30 = 90, not 100
            "social_unrest_pct": 50.0,
            "social_cohesion_pct": 50.0,
            "environmental_degradation_pct": 50.0,
            "environmental_resilience_pct": 50.0,
            "political_instability_pct": 50.0,
            "political_stability_pct": 50.0,
            "technological_disruption_pct": 50.0,
            "technological_advancement_pct": 50.0
        }
        
        success, response = self.run_test(
            "Create Scenario Adjustment - Invalid Percentages",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            400,
            data=invalid_adjustment_data
        )
        
        if success:
            print(f"   ✅ Percentage validation working - Invalid percentages correctly rejected")
            return True
        else:
            print(f"   ❌ Percentage validation failed")
            return False

    def test_get_scenario_adjustments(self):
        """Test Retrieving Scenario Adjustments"""
        success, response = self.run_test(
            "Get Scenario Adjustments",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} scenario adjustments")
            return True
        else:
            return False

    def test_update_scenario_adjustment(self):
        """Test Updating Scenario Adjustment"""
        if not self.scenario_adjustment_id:
            print("❌ No scenario adjustment ID available")
            return False
            
        update_data = {
            "adjustment_name": "Updated Crisis Scenario",
            "economic_crisis_pct": 75.0,
            "economic_stability_pct": 25.0,
            "social_unrest_pct": 40.0,
            "social_cohesion_pct": 60.0,
            "environmental_degradation_pct": 90.0,
            "environmental_resilience_pct": 10.0,
            "political_instability_pct": 55.0,
            "political_stability_pct": 45.0,
            "technological_disruption_pct": 35.0,
            "technological_advancement_pct": 65.0
        }
        
        success, response = self.run_test(
            "Update Scenario Adjustment",
            "PUT",
            f"companies/{self.company_id}/scenario-adjustments/{self.scenario_adjustment_id}",
            200,
            data=update_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Scenario adjustment updated successfully")
            print(f"   Updated name: {response.get('adjustment_name', 'N/A')}")
            print(f"   New economic crisis %: {response.get('economic_crisis_pct', 'N/A')}")
            return True
        else:
            return False

    def test_create_consensus(self):
        """Test Creating Consensus Settings"""
        if not self.scenario_adjustment_id:
            print("❌ No scenario adjustment ID available")
            return False
            
        consensus_data = {
            "adjustment_id": self.scenario_adjustment_id,
            "consensus_name": "Crisis Response Team Consensus"
        }
        
        success, response = self.run_test(
            "Create Consensus Settings",
            "POST",
            f"companies/{self.company_id}/consensus",
            200,
            data=consensus_data
        )
        
        if success and 'id' in response:
            self.consensus_id = response['id']
            print(f"   ✅ Consensus created with ID: {self.consensus_id}")
            print(f"   Consensus percentage: {response.get('consensus_percentage', 'N/A')}%")
            return True
        else:
            return False

    def test_agree_to_consensus(self):
        """Test User Agreement to Consensus"""
        if not self.consensus_id:
            print("❌ No consensus ID available")
            return False
            
        success, response = self.run_test(
            "Agree to Consensus",
            "POST",
            f"companies/{self.company_id}/consensus/{self.consensus_id}/agree",
            200
        )
        
        if success:
            print(f"   ✅ Agreement recorded successfully")
            print(f"   Consensus reached: {response.get('consensus_reached', 'N/A')}")
            return True
        else:
            return False

def main():
    print("🎯 Testing Fuzzy Logic Scenario Adjusters Endpoints")
    print("=" * 60)
    
    tester = FuzzyLogicTester()
    
    # Setup test environment
    print("\n📝 Setting up test environment...")
    if not tester.setup_test_environment():
        print("❌ Failed to setup test environment")
        return 1

    # Run Fuzzy Logic tests
    print("\n🎯 Testing Fuzzy Logic Scenario Adjusters...")
    
    tests = [
        tester.test_create_scenario_adjustment,
        tester.test_percentage_validation,
        tester.test_get_scenario_adjustments,
        tester.test_update_scenario_adjustment,
        tester.test_create_consensus,
        tester.test_agree_to_consensus
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Fuzzy Logic Tests: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Fuzzy Logic tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())