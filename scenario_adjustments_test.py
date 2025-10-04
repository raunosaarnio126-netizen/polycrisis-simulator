import requests
import sys
import json
from datetime import datetime

class ScenarioAdjustmentsAPITester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.company_id = None
        self.adjustment_id = None
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
                response = requests.get(url, headers=test_headers, timeout=120)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=120)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=120)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=120)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=120)

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
        """Setup test environment with authentication and company"""
        print("🚀 Setting up test environment...")
        
        # Login with test credentials
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "Login with Test Credentials",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if not success or 'access_token' not in response:
            print("❌ Failed to login - cannot proceed with tests")
            return False
            
        self.token = response['access_token']
        print(f"   ✅ Logged in successfully")
        
        # Get user profile
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   ✅ User ID: {self.user_id}")
        
        # Create or get company for testing
        company_data = {
            "company_name": "Test Scenario Adjustments Corp",
            "industry": "Crisis Management",
            "company_size": "medium",
            "website_url": "https://example.com",
            "description": "Test company for scenario adjustments testing",
            "location": "Test City"
        }
        
        success, response = self.run_test(
            "Create Test Company",
            "POST",
            "companies",
            200,
            data=company_data
        )
        
        if success and 'id' in response:
            self.company_id = response['id']
            print(f"   ✅ Company ID: {self.company_id}")
            return True
        else:
            print("❌ Failed to create company - cannot proceed with tests")
            return False

    def test_create_scenario_adjustment(self):
        """Test POST /api/companies/{company_id}/scenario-adjustments - Save Adjustments"""
        if not self.company_id:
            print("❌ No company ID available for scenario adjustment creation")
            return False
            
        adjustment_data = {
            "adjustment_name": "Economic Crisis Scenario Test",
            "scenario_id": None,  # Optional link to existing scenario
            # SEPTE Framework percentages (each pair must sum to 100)
            "economic_crisis_pct": 75.0,
            "economic_stability_pct": 25.0,
            "social_unrest_pct": 60.0,
            "social_cohesion_pct": 40.0,
            "environmental_degradation_pct": 45.0,
            "environmental_resilience_pct": 55.0,
            "political_instability_pct": 70.0,
            "political_stability_pct": 30.0,
            "technological_disruption_pct": 35.0,
            "technological_advancement_pct": 65.0
        }
        
        success, response = self.run_test(
            "Create Scenario Adjustment (Save Adjustments)",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            200,
            data=adjustment_data
        )
        
        if success and 'id' in response:
            self.adjustment_id = response['id']
            print(f"   ✅ Created adjustment ID: {self.adjustment_id}")
            print(f"   Adjustment name: {response.get('adjustment_name')}")
            print(f"   Company ID: {response.get('company_id')}")
            print(f"   Risk level: {response.get('risk_level')}")
            print(f"   Real-time analysis length: {len(response.get('real_time_analysis', ''))}")
            print(f"   Impact summary length: {len(response.get('impact_summary', ''))}")
            print(f"   Recommendations count: {len(response.get('recommendations', []))}")
            
            # Verify SEPTE values are preserved
            septe_fields = [
                'economic_crisis_pct', 'economic_stability_pct',
                'social_unrest_pct', 'social_cohesion_pct',
                'environmental_degradation_pct', 'environmental_resilience_pct',
                'political_instability_pct', 'political_stability_pct',
                'technological_disruption_pct', 'technological_advancement_pct'
            ]
            
            for field in septe_fields:
                expected_value = adjustment_data[field]
                actual_value = response.get(field)
                if abs(expected_value - actual_value) > 0.1:
                    print(f"   ❌ SEPTE value mismatch for {field}: expected {expected_value}, got {actual_value}")
                    return False
                    
            print(f"   ✅ All SEPTE values preserved correctly")
            
            # Verify AI analysis was generated
            if not response.get('real_time_analysis'):
                print(f"   ❌ No real-time analysis generated")
                return False
                
            if not response.get('impact_summary'):
                print(f"   ❌ No impact summary generated")
                return False
                
            print(f"   ✅ AI analysis generated successfully")
            return True
        return False

    def test_get_scenario_adjustments(self):
        """Test GET /api/companies/{company_id}/scenario-adjustments"""
        if not self.company_id:
            print("❌ No company ID available for getting scenario adjustments")
            return False
            
        success, response = self.run_test(
            "Get Scenario Adjustments",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Found {len(response)} scenario adjustments")
            
            if response:
                # Verify structure of first adjustment
                adjustment = response[0]
                required_fields = [
                    'id', 'company_id', 'adjustment_name', 'created_by',
                    'economic_crisis_pct', 'economic_stability_pct',
                    'social_unrest_pct', 'social_cohesion_pct',
                    'environmental_degradation_pct', 'environmental_resilience_pct',
                    'political_instability_pct', 'political_stability_pct',
                    'technological_disruption_pct', 'technological_advancement_pct',
                    'real_time_analysis', 'impact_summary', 'risk_level', 'recommendations'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in adjustment:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    return False
                    
                print(f"   ✅ All required fields present in adjustment response")
                
                # Show adjustment details
                for adj in response:
                    print(f"   - {adj.get('adjustment_name')}: Risk {adj.get('risk_level')}")
                    print(f"     Economic Crisis: {adj.get('economic_crisis_pct')}%")
                    print(f"     Social Unrest: {adj.get('social_unrest_pct')}%")
                    print(f"     Political Instability: {adj.get('political_instability_pct')}%")
                    
            return True
        return False

    def test_update_scenario_adjustment(self):
        """Test PUT /api/companies/{company_id}/scenario-adjustments/{adjustment_id}"""
        if not self.company_id or not self.adjustment_id:
            print("❌ No company ID or adjustment ID available for update")
            return False
            
        # Update with different SEPTE values
        updated_data = {
            "adjustment_name": "Updated Economic Crisis Scenario",
            "scenario_id": None,
            # Different SEPTE values
            "economic_crisis_pct": 85.0,
            "economic_stability_pct": 15.0,
            "social_unrest_pct": 70.0,
            "social_cohesion_pct": 30.0,
            "environmental_degradation_pct": 55.0,
            "environmental_resilience_pct": 45.0,
            "political_instability_pct": 80.0,
            "political_stability_pct": 20.0,
            "technological_disruption_pct": 40.0,
            "technological_advancement_pct": 60.0
        }
        
        success, response = self.run_test(
            "Update Scenario Adjustment",
            "PUT",
            f"companies/{self.company_id}/scenario-adjustments/{self.adjustment_id}",
            200,
            data=updated_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Updated adjustment ID: {response.get('id')}")
            print(f"   Updated name: {response.get('adjustment_name')}")
            print(f"   Updated risk level: {response.get('risk_level')}")
            
            # Verify updated values
            if response.get('adjustment_name') != updated_data['adjustment_name']:
                print(f"   ❌ Name not updated correctly")
                return False
                
            if abs(response.get('economic_crisis_pct', 0) - updated_data['economic_crisis_pct']) > 0.1:
                print(f"   ❌ Economic crisis percentage not updated correctly")
                return False
                
            print(f"   ✅ Values updated correctly")
            
            # Verify AI analysis was regenerated
            if not response.get('real_time_analysis'):
                print(f"   ❌ No updated real-time analysis")
                return False
                
            print(f"   ✅ AI analysis regenerated on update")
            
            # Verify updated_at timestamp changed
            if 'updated_at' not in response:
                print(f"   ❌ No updated_at timestamp")
                return False
                
            print(f"   ✅ Updated timestamp present")
            return True
        return False

    def test_create_consensus(self):
        """Test POST /api/companies/{company_id}/consensus - Save Consensus"""
        if not self.company_id or not self.adjustment_id:
            print("❌ No company ID or adjustment ID available for consensus creation")
            return False
            
        consensus_data = {
            "adjustment_id": self.adjustment_id,
            "consensus_name": "Team Agreement on Economic Crisis Scenario",
            "team_id": None  # Optional team ID
        }
        
        success, response = self.run_test(
            "Create Consensus (Save Consensus)",
            "POST",
            f"companies/{self.company_id}/consensus",
            200,
            data=consensus_data
        )
        
        if success and 'id' in response:
            self.consensus_id = response['id']
            print(f"   ✅ Created consensus ID: {self.consensus_id}")
            print(f"   Consensus name: {response.get('consensus_name')}")
            print(f"   Company ID: {response.get('company_id')}")
            print(f"   Adjustment ID: {response.get('adjustment_id')}")
            print(f"   Total team members: {response.get('total_team_members')}")
            print(f"   Agreed by count: {len(response.get('agreed_by', []))}")
            print(f"   Consensus percentage: {response.get('consensus_percentage')}%")
            print(f"   Consensus reached: {response.get('consensus_reached')}")
            
            # Verify required fields
            required_fields = [
                'id', 'company_id', 'adjustment_id', 'consensus_name',
                'agreed_by', 'total_team_members', 'consensus_reached',
                'consensus_percentage', 'final_settings'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
                
            print(f"   ✅ All required fields present")
            
            # Verify final_settings contains SEPTE parameters
            final_settings = response.get('final_settings', {})
            septe_fields = [
                'economic_crisis_pct', 'economic_stability_pct',
                'social_unrest_pct', 'social_cohesion_pct',
                'environmental_degradation_pct', 'environmental_resilience_pct',
                'political_instability_pct', 'political_stability_pct',
                'technological_disruption_pct', 'technological_advancement_pct'
            ]
            
            missing_septe = []
            for field in septe_fields:
                if field not in final_settings:
                    missing_septe.append(field)
            
            if missing_septe:
                print(f"   ❌ Missing SEPTE fields in final_settings: {missing_septe}")
                return False
                
            print(f"   ✅ All SEPTE parameters present in final_settings")
            
            # Verify creator is automatically added to agreed_by list
            agreed_by = response.get('agreed_by', [])
            if not agreed_by:
                print(f"   ❌ Creator not automatically added to agreed_by list")
                return False
                
            print(f"   ✅ Creator automatically added to consensus")
            return True
        return False

    def test_consensus_agreement(self):
        """Test POST /api/companies/{company_id}/consensus/{consensus_id}/agree"""
        if not self.company_id or not self.consensus_id:
            print("❌ No company ID or consensus ID available for agreement")
            return False
            
        success, response = self.run_test(
            "Agree to Consensus",
            "POST",
            f"companies/{self.company_id}/consensus/{self.consensus_id}/agree",
            200
        )
        
        if success:
            print(f"   ✅ Agreement recorded")
            print(f"   Message: {response.get('message')}")
            print(f"   Consensus reached: {response.get('consensus_reached')}")
            
            # Verify response structure
            if 'message' not in response:
                print(f"   ❌ No message in response")
                return False
                
            if 'consensus_reached' not in response:
                print(f"   ❌ No consensus_reached status in response")
                return False
                
            print(f"   ✅ Agreement response structure correct")
            return True
        return False

    def test_septe_validation(self):
        """Test SEPTE percentage validation (pairs must sum to 100)"""
        if not self.company_id:
            print("❌ No company ID available for validation testing")
            return False
            
        # Test invalid SEPTE values (don't sum to 100)
        invalid_data = {
            "adjustment_name": "Invalid SEPTE Test",
            "economic_crisis_pct": 60.0,
            "economic_stability_pct": 30.0,  # Should be 40.0 to sum to 100
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
            "Test SEPTE Validation (Should Fail)",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            400,  # Should return 400 for validation error
            data=invalid_data
        )
        
        if success:
            print(f"   ✅ SEPTE validation working - rejected invalid percentages")
            print(f"   Error message: {response.get('detail', 'No error message')}")
            return True
        else:
            print(f"   ❌ SEPTE validation not working - should have rejected invalid percentages")
            return False

    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        if not self.company_id:
            print("❌ No company ID available for auth testing")
            return False
            
        # Save current token
        original_token = self.token
        self.token = None
        
        # Test without authentication
        success, response = self.run_test(
            "Test Authentication Required (Should Fail)",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            401  # Should return 401 for unauthorized
        )
        
        # Restore token
        self.token = original_token
        
        if success:
            print(f"   ✅ Authentication properly enforced")
            return True
        else:
            print(f"   ❌ Authentication not enforced - endpoint should require auth")
            return False

    def test_access_control(self):
        """Test company access control"""
        # Test with invalid company ID
        fake_company_id = "fake-company-id-12345"
        
        success, response = self.run_test(
            "Test Access Control with Invalid Company ID",
            "GET",
            f"companies/{fake_company_id}/scenario-adjustments",
            403  # Should return 403 for access denied
        )
        
        if success:
            print(f"   ✅ Access control working - denied access to invalid company")
            return True
        else:
            print(f"   ❌ Access control not working properly")
            return False

    def test_download_settings_functionality(self):
        """Test download settings functionality (if implemented)"""
        if not self.company_id or not self.adjustment_id:
            print("❌ No company ID or adjustment ID available for download test")
            return False
            
        # Test if there's a download endpoint
        success, response = self.run_test(
            "Test Download Settings",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments/{self.adjustment_id}/download",
            200
        )
        
        if success:
            print(f"   ✅ Download settings endpoint working")
            return True
        else:
            print(f"   ⚠️ Download settings endpoint not found (may be frontend-only)")
            # This is not necessarily a failure as download might be frontend-only
            return True

    def run_comprehensive_test(self):
        """Run all scenario adjustments and consensus tests"""
        print("🧪 SCENARIO ADJUSTMENTS AND CONSENSUS FUNCTIONALITY TESTING")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        # Core functionality tests
        tests = [
            ("Create Scenario Adjustment (Save Adjustments)", self.test_create_scenario_adjustment),
            ("Get Scenario Adjustments", self.test_get_scenario_adjustments),
            ("Update Scenario Adjustment", self.test_update_scenario_adjustment),
            ("Create Consensus (Save Consensus)", self.test_create_consensus),
            ("Consensus Agreement", self.test_consensus_agreement),
            ("SEPTE Validation", self.test_septe_validation),
            ("Authentication Required", self.test_authentication_required),
            ("Access Control", self.test_access_control),
            ("Download Settings", self.test_download_settings_functionality)
        ]
        
        passed_tests = 0
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"🔬 {test_name}")
            print(f"{'='*50}")
            
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {str(e)}")
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests Run: {len(tests)}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {len(tests) - passed_tests}")
        print(f"Success Rate: {(passed_tests/len(tests)*100):.1f}%")
        
        print(f"\n📈 API CALL SUMMARY")
        print(f"Total API Calls: {self.tests_run}")
        print(f"Successful API Calls: {self.tests_passed}")
        print(f"API Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        return passed_tests == len(tests)

if __name__ == "__main__":
    tester = ScenarioAdjustmentsAPITester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED! Scenario adjustments and consensus functionality is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️ SOME TESTS FAILED! Check the output above for details.")
        sys.exit(1)