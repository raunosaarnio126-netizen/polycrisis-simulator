import requests
import sys
import json
from datetime import datetime

class ComprehensiveFuzzyLogicTester:
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
            "email": f"comprehensive_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"compuser_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Comprehensive Test Org"
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
        else:
            return False

        # Create company
        company_data = {
            "company_name": "Comprehensive Fuzzy Logic Test Corp",
            "industry": "Crisis Management",
            "company_size": "large",
            "website_url": "https://crisistest.com",
            "description": "A comprehensive test company for advanced fuzzy logic scenario adjustments",
            "location": "New York, NY"
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
            return True
        else:
            return False

    def test_extreme_septe_scenarios(self):
        """Test Various Extreme SEPTE Scenarios"""
        scenarios = [
            {
                "name": "Maximum Crisis Scenario",
                "data": {
                    "adjustment_name": "Maximum Crisis - All Systems Failing",
                    "economic_crisis_pct": 95.0, "economic_stability_pct": 5.0,
                    "social_unrest_pct": 90.0, "social_cohesion_pct": 10.0,
                    "environmental_degradation_pct": 85.0, "environmental_resilience_pct": 15.0,
                    "political_instability_pct": 80.0, "political_stability_pct": 20.0,
                    "technological_disruption_pct": 75.0, "technological_advancement_pct": 25.0
                },
                "expected_risk": ["high", "critical"]
            },
            {
                "name": "Stability Scenario",
                "data": {
                    "adjustment_name": "High Stability - Resilient Systems",
                    "economic_crisis_pct": 10.0, "economic_stability_pct": 90.0,
                    "social_unrest_pct": 5.0, "social_cohesion_pct": 95.0,
                    "environmental_degradation_pct": 15.0, "environmental_resilience_pct": 85.0,
                    "political_instability_pct": 20.0, "political_stability_pct": 80.0,
                    "technological_disruption_pct": 25.0, "technological_advancement_pct": 75.0
                },
                "expected_risk": ["low", "medium"]
            },
            {
                "name": "Mixed Scenario",
                "data": {
                    "adjustment_name": "Mixed Crisis - Economic Focus",
                    "economic_crisis_pct": 70.0, "economic_stability_pct": 30.0,
                    "social_unrest_pct": 40.0, "social_cohesion_pct": 60.0,
                    "environmental_degradation_pct": 50.0, "environmental_resilience_pct": 50.0,
                    "political_instability_pct": 35.0, "political_stability_pct": 65.0,
                    "technological_disruption_pct": 45.0, "technological_advancement_pct": 55.0
                },
                "expected_risk": ["medium", "high"]
            }
        ]
        
        successful_scenarios = 0
        
        for scenario in scenarios:
            success, response = self.run_test(
                f"Create {scenario['name']}",
                "POST",
                f"companies/{self.company_id}/scenario-adjustments",
                200,
                data=scenario['data']
            )
            
            if success and 'id' in response:
                successful_scenarios += 1
                risk_level = response.get('risk_level', '')
                analysis_length = len(response.get('real_time_analysis', ''))
                recommendations_count = len(response.get('recommendations', []))
                
                print(f"   ✅ {scenario['name']} created successfully")
                print(f"   Risk Level: {risk_level}")
                print(f"   Analysis Length: {analysis_length} characters")
                print(f"   Recommendations: {recommendations_count}")
                
                # Verify risk level is appropriate
                if risk_level in scenario['expected_risk']:
                    print(f"   ✅ Risk level '{risk_level}' is appropriate")
                else:
                    print(f"   ⚠️ Risk level '{risk_level}' not in expected range {scenario['expected_risk']}")
                
                # Verify AI analysis quality
                if analysis_length > 500:
                    print(f"   ✅ Comprehensive AI analysis generated")
                else:
                    print(f"   ⚠️ AI analysis seems short for complex scenario")
                
                # Store first scenario ID for later tests
                if not hasattr(self, 'scenario_adjustment_id'):
                    self.scenario_adjustment_id = response['id']
            else:
                print(f"   ❌ Failed to create {scenario['name']}")
        
        print(f"\n   Successfully created {successful_scenarios}/{len(scenarios)} extreme scenarios")
        return successful_scenarios == len(scenarios)

    def test_percentage_edge_cases(self):
        """Test Edge Cases for Percentage Validation"""
        edge_cases = [
            {
                "name": "Floating Point Precision",
                "data": {
                    "adjustment_name": "Floating Point Test",
                    "economic_crisis_pct": 33.33, "economic_stability_pct": 66.67,
                    "social_unrest_pct": 50.0, "social_cohesion_pct": 50.0,
                    "environmental_degradation_pct": 50.0, "environmental_resilience_pct": 50.0,
                    "political_instability_pct": 50.0, "political_stability_pct": 50.0,
                    "technological_disruption_pct": 50.0, "technological_advancement_pct": 50.0
                },
                "expected_status": 200  # Should pass with small floating point error
            },
            {
                "name": "Zero Values",
                "data": {
                    "adjustment_name": "Zero Values Test",
                    "economic_crisis_pct": 0.0, "economic_stability_pct": 100.0,
                    "social_unrest_pct": 100.0, "social_cohesion_pct": 0.0,
                    "environmental_degradation_pct": 50.0, "environmental_resilience_pct": 50.0,
                    "political_instability_pct": 50.0, "political_stability_pct": 50.0,
                    "technological_disruption_pct": 50.0, "technological_advancement_pct": 50.0
                },
                "expected_status": 200  # Should pass
            },
            {
                "name": "Large Deviation",
                "data": {
                    "adjustment_name": "Large Deviation Test",
                    "economic_crisis_pct": 60.0, "economic_stability_pct": 30.0,  # Sum = 90
                    "social_unrest_pct": 50.0, "social_cohesion_pct": 50.0,
                    "environmental_degradation_pct": 50.0, "environmental_resilience_pct": 50.0,
                    "political_instability_pct": 50.0, "political_stability_pct": 50.0,
                    "technological_disruption_pct": 50.0, "technological_advancement_pct": 50.0
                },
                "expected_status": 400  # Should fail
            }
        ]
        
        successful_tests = 0
        
        for case in edge_cases:
            success, response = self.run_test(
                f"Percentage Edge Case - {case['name']}",
                "POST",
                f"companies/{self.company_id}/scenario-adjustments",
                case['expected_status'],
                data=case['data']
            )
            
            if success:
                successful_tests += 1
                if case['expected_status'] == 200:
                    print(f"   ✅ {case['name']} correctly accepted")
                else:
                    print(f"   ✅ {case['name']} correctly rejected")
            else:
                print(f"   ❌ {case['name']} validation failed")
        
        print(f"\n   Passed {successful_tests}/{len(edge_cases)} edge case tests")
        return successful_tests == len(edge_cases)

    def test_access_control_comprehensive(self):
        """Test Comprehensive Access Control"""
        # Create unauthorized user
        unauthorized_user_data = {
            "email": f"unauthorized_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"unauth_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Unauthorized Org"
        }
        
        success, response = self.run_test(
            "Register Unauthorized User",
            "POST",
            "register",
            200,
            data=unauthorized_user_data
        )
        
        if not success:
            print("❌ Could not create unauthorized user")
            return False
        
        # Store original token
        original_token = self.token
        unauthorized_token = response.get('access_token')
        
        # Test unauthorized access to various endpoints
        unauthorized_tests = [
            ("GET Scenario Adjustments", "GET", f"companies/{self.company_id}/scenario-adjustments", 403),
            ("CREATE Scenario Adjustment", "POST", f"companies/{self.company_id}/scenario-adjustments", 403),
            ("UPDATE Scenario Adjustment", "PUT", f"companies/{self.company_id}/scenario-adjustments/fake-id", 403),
            ("CREATE Consensus", "POST", f"companies/{self.company_id}/consensus", 403),
            ("AGREE to Consensus", "POST", f"companies/{self.company_id}/consensus/fake-id/agree", 403)
        ]
        
        # Switch to unauthorized token
        self.token = unauthorized_token
        
        successful_blocks = 0
        
        for test_name, method, endpoint, expected_status in unauthorized_tests:
            test_data = {
                "adjustment_name": "Unauthorized Test",
                "economic_crisis_pct": 50.0, "economic_stability_pct": 50.0,
                "social_unrest_pct": 50.0, "social_cohesion_pct": 50.0,
                "environmental_degradation_pct": 50.0, "environmental_resilience_pct": 50.0,
                "political_instability_pct": 50.0, "political_stability_pct": 50.0,
                "technological_disruption_pct": 50.0, "technological_advancement_pct": 50.0
            } if method in ["POST", "PUT"] else None
            
            success, response = self.run_test(
                f"Unauthorized {test_name}",
                method,
                endpoint,
                expected_status,
                data=test_data
            )
            
            if success:
                successful_blocks += 1
                print(f"   ✅ Unauthorized access correctly blocked for {test_name}")
            else:
                print(f"   ❌ Unauthorized access allowed for {test_name}")
        
        # Restore original token
        self.token = original_token
        
        print(f"\n   Successfully blocked {successful_blocks}/{len(unauthorized_tests)} unauthorized attempts")
        return successful_blocks == len(unauthorized_tests)

    def test_ai_analysis_quality(self):
        """Test AI Analysis Quality and Content"""
        if not self.scenario_adjustment_id:
            print("❌ No scenario adjustment available for AI analysis test")
            return False
        
        # Get the scenario adjustment to analyze AI content
        success, response = self.run_test(
            "Get Scenario Adjustment for AI Analysis",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if not success or not response:
            print("❌ Could not retrieve scenario adjustments")
            return False
        
        # Find our adjustment
        adjustment = None
        for adj in response:
            if adj.get('id') == self.scenario_adjustment_id:
                adjustment = adj
                break
        
        if not adjustment:
            print("❌ Could not find test scenario adjustment")
            return False
        
        # Analyze AI content quality
        analysis = adjustment.get('real_time_analysis', '')
        impact_summary = adjustment.get('impact_summary', '')
        recommendations = adjustment.get('recommendations', [])
        risk_level = adjustment.get('risk_level', '')
        
        print(f"   AI Analysis Quality Assessment:")
        print(f"   - Analysis length: {len(analysis)} characters")
        print(f"   - Impact summary length: {len(impact_summary)} characters")
        print(f"   - Recommendations count: {len(recommendations)}")
        print(f"   - Risk level: {risk_level}")
        
        quality_checks = []
        
        # Check analysis length
        if len(analysis) > 200:
            quality_checks.append("✅ Substantial analysis content")
        else:
            quality_checks.append("⚠️ Analysis content seems short")
        
        # Check impact summary
        if len(impact_summary) > 50:
            quality_checks.append("✅ Meaningful impact summary")
        else:
            quality_checks.append("⚠️ Impact summary seems short")
        
        # Check recommendations
        if len(recommendations) >= 3:
            quality_checks.append("✅ Multiple recommendations provided")
        else:
            quality_checks.append("⚠️ Few recommendations provided")
        
        # Check risk level validity
        if risk_level in ['low', 'medium', 'high', 'critical']:
            quality_checks.append("✅ Valid risk level assigned")
        else:
            quality_checks.append("⚠️ Invalid risk level")
        
        # Check for SEPTE-related content
        septe_terms = ['economic', 'social', 'environmental', 'political', 'technological']
        septe_mentions = sum(1 for term in septe_terms if term.lower() in analysis.lower())
        
        if septe_mentions >= 3:
            quality_checks.append("✅ SEPTE framework referenced in analysis")
        else:
            quality_checks.append("⚠️ Limited SEPTE framework integration")
        
        for check in quality_checks:
            print(f"   {check}")
        
        # Count successful quality checks
        successful_checks = sum(1 for check in quality_checks if check.startswith("✅"))
        total_checks = len(quality_checks)
        
        print(f"\n   AI Analysis Quality: {successful_checks}/{total_checks} checks passed")
        return successful_checks >= (total_checks * 0.8)  # 80% pass rate

def main():
    print("🎯 Comprehensive Fuzzy Logic Scenario Adjusters Testing")
    print("=" * 70)
    
    tester = ComprehensiveFuzzyLogicTester()
    
    # Setup test environment
    print("\n📝 Setting up comprehensive test environment...")
    if not tester.setup_test_environment():
        print("❌ Failed to setup test environment")
        return 1

    # Run comprehensive tests
    print("\n🎯 Running Comprehensive Fuzzy Logic Tests...")
    
    tests = [
        ("Extreme SEPTE Scenarios", tester.test_extreme_septe_scenarios),
        ("Percentage Edge Cases", tester.test_percentage_edge_cases),
        ("Access Control Comprehensive", tester.test_access_control_comprehensive),
        ("AI Analysis Quality", tester.test_ai_analysis_quality)
    ]
    
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"\n🔬 Testing {test_name}...")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED with exception: {e}")

    # Print results
    print("\n" + "=" * 70)
    print(f"📊 Comprehensive Tests: {passed_tests}/{len(tests)} test suites passed")
    print(f"📊 Individual API Tests: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if passed_tests == len(tests):
        print("🎉 All comprehensive Fuzzy Logic tests passed!")
        return 0
    else:
        print(f"⚠️  {len(tests) - passed_tests} test suites failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())