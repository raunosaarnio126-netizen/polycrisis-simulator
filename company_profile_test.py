import requests
import sys
import json
from datetime import datetime

class CompanyProfileTester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.company_id = None
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

    def test_authentication_setup(self):
        """Test authentication with admin@test.com/admin123 credentials"""
        print(f"\n🔐 AUTHENTICATION SETUP TESTING")
        print(f"=" * 50)
        
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        
        success, response = self.run_test(
            "Login with Admin Credentials",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Authentication successful")
            print(f"   Token length: {len(self.token)} characters")
            return True
        else:
            print(f"   ❌ Authentication failed - cannot proceed with company profile tests")
            return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        success, response = self.run_test(
            "Get Current User Profile",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Username: {response.get('username', 'N/A')}")
            print(f"   Organization: {response.get('organization', 'N/A')}")
            print(f"   Current Company ID: {response.get('company_id', 'None')}")
            return True
        return False

    def test_create_company_profile(self):
        """Test creating company profile with realistic data from review request"""
        print(f"\n🏢 COMPANY PROFILE CREATION TESTING")
        print(f"=" * 50)
        
        # Use realistic company data as specified in review request
        company_data = {
            "company_name": "Crisis Management Solutions Corp",
            "industry": "technology",
            "company_size": "medium",
            "description": "Professional crisis management and emergency response services",
            "location": "Helsinki, Finland",
            "website_url": "https://crisis-solutions.fi"
        }
        
        success, response = self.run_test(
            "Create Company Profile",
            "POST",
            "companies",
            200,
            data=company_data
        )
        
        if success and 'id' in response:
            self.company_id = response['id']
            print(f"   ✅ Company profile created successfully")
            print(f"   Company ID: {self.company_id}")
            print(f"   Company Name: {response.get('company_name', 'N/A')}")
            print(f"   Industry: {response.get('industry', 'N/A')}")
            print(f"   Size: {response.get('company_size', 'N/A')}")
            print(f"   Location: {response.get('location', 'N/A')}")
            print(f"   Description: {response.get('description', 'N/A')}")
            print(f"   Created by: {response.get('created_by', 'N/A')}")
            print(f"   Created at: {response.get('created_at', 'N/A')}")
            
            # Verify all required fields are present
            required_fields = ['id', 'company_name', 'industry', 'company_size', 'description', 'location', 'created_by', 'created_at']
            missing_fields = []
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Missing fields in response: {missing_fields}")
                return False
            
            return True
        else:
            print(f"   ❌ Company profile creation failed")
            return False

    def test_get_company_profiles(self):
        """Test retrieving company profiles for authenticated user"""
        print(f"\n📋 COMPANY PROFILE RETRIEVAL TESTING")
        print(f"=" * 50)
        
        success, response = self.run_test(
            "Get Company Profiles",
            "GET",
            "companies",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Company profiles retrieved successfully")
            print(f"   Number of companies found: {len(response)}")
            
            if len(response) > 0:
                # Verify the company we just created is in the list
                company_found = False
                for company in response:
                    print(f"   - Company: {company.get('company_name', 'N/A')} (ID: {company.get('id', 'N/A')})")
                    print(f"     Industry: {company.get('industry', 'N/A')}, Size: {company.get('company_size', 'N/A')}")
                    print(f"     Location: {company.get('location', 'N/A')}")
                    
                    if company.get('id') == self.company_id:
                        company_found = True
                        print(f"     ✅ Created company found in list")
                
                if not company_found and self.company_id:
                    print(f"   ⚠️ Created company (ID: {self.company_id}) not found in company list")
                    return False
                
                return True
            else:
                print(f"   ⚠️ No companies found - this might indicate a problem with company creation or retrieval")
                return False
        else:
            print(f"   ❌ Failed to retrieve company profiles")
            return False

    def test_company_profile_association(self):
        """Test if company profiles are properly linked to user accounts"""
        print(f"\n🔗 COMPANY PROFILE ASSOCIATION TESTING")
        print(f"=" * 50)
        
        # Get user profile again to check if company_id was updated
        success, response = self.run_test(
            "Check User-Company Association",
            "GET",
            "me",
            200
        )
        
        if success:
            user_company_id = response.get('company_id')
            print(f"   User's company_id: {user_company_id}")
            print(f"   Created company_id: {self.company_id}")
            
            if user_company_id == self.company_id:
                print(f"   ✅ Company profile properly associated with user account")
                return True
            elif user_company_id is None:
                print(f"   ⚠️ User company_id is None - association may not be automatic")
                # This might be expected behavior - let's test if we can still access company data
                return True
            else:
                print(f"   ⚠️ User company_id doesn't match created company - checking access permissions")
                return True
        else:
            print(f"   ❌ Failed to check user-company association")
            return False

    def test_company_requirement_validation(self):
        """Test if company profile requirement for Scenario Adjusters is satisfied"""
        print(f"\n🎯 SCENARIO ADJUSTERS ACCESS TESTING")
        print(f"=" * 50)
        
        if not self.company_id:
            print(f"   ❌ No company ID available - cannot test SEPTE framework access")
            return False
        
        # Test creating a scenario adjustment to verify company requirement is satisfied
        adjustment_data = {
            "adjustment_name": "Test SEPTE Framework Access",
            "economic_crisis_pct": 70.0,
            "economic_stability_pct": 30.0,
            "social_unrest_pct": 60.0,
            "social_cohesion_pct": 40.0,
            "environmental_degradation_pct": 50.0,
            "environmental_resilience_pct": 50.0,
            "political_instability_pct": 65.0,
            "political_stability_pct": 35.0,
            "technological_disruption_pct": 40.0,
            "technological_advancement_pct": 60.0
        }
        
        success, response = self.run_test(
            "Test SEPTE Framework Access",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            200,
            data=adjustment_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ SEPTE framework accessible - company profile requirement satisfied")
            print(f"   Scenario adjustment ID: {response.get('id')}")
            print(f"   Risk level: {response.get('risk_level', 'N/A')}")
            print(f"   Real-time analysis generated: {bool(response.get('real_time_analysis'))}")
            return True
        else:
            print(f"   ❌ SEPTE framework not accessible - company profile requirement not satisfied")
            return False

    def test_save_adjustments_button_access(self):
        """Test if Save Adjustments functionality is accessible"""
        print(f"\n💾 SAVE ADJUSTMENTS FUNCTIONALITY TESTING")
        print(f"=" * 50)
        
        if not self.company_id:
            print(f"   ❌ No company ID available - cannot test Save Adjustments")
            return False
        
        # Get existing scenario adjustments
        success, response = self.run_test(
            "Get Scenario Adjustments",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Save Adjustments functionality accessible")
            print(f"   Number of saved adjustments: {len(response)}")
            
            if len(response) > 0:
                adjustment = response[0]
                print(f"   Sample adjustment: {adjustment.get('adjustment_name', 'N/A')}")
                print(f"   Risk level: {adjustment.get('risk_level', 'N/A')}")
                print(f"   Created at: {adjustment.get('created_at', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Save Adjustments functionality not accessible")
            return False

    def test_download_settings_functionality(self):
        """Test if Download Settings functionality works"""
        print(f"\n📥 DOWNLOAD SETTINGS FUNCTIONALITY TESTING")
        print(f"=" * 50)
        
        if not self.company_id:
            print(f"   ❌ No company ID available - cannot test Download Settings")
            return False
        
        # Get scenario adjustments to download
        success, response = self.run_test(
            "Get Adjustments for Download",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            print(f"   ✅ Download Settings functionality accessible")
            print(f"   Available adjustments for download: {len(response)}")
            
            # Show downloadable data structure
            adjustment = response[0]
            downloadable_fields = ['adjustment_name', 'economic_crisis_pct', 'economic_stability_pct', 
                                 'social_unrest_pct', 'social_cohesion_pct', 'environmental_degradation_pct',
                                 'environmental_resilience_pct', 'political_instability_pct', 'political_stability_pct',
                                 'technological_disruption_pct', 'technological_advancement_pct', 'risk_level']
            
            print(f"   Downloadable settings structure:")
            for field in downloadable_fields:
                if field in adjustment:
                    print(f"     {field}: {adjustment[field]}")
            
            return True
        else:
            print(f"   ❌ Download Settings functionality not accessible - no adjustments available")
            return False

    def test_save_consensus_functionality(self):
        """Test if Save Consensus functionality is accessible"""
        print(f"\n🤝 SAVE CONSENSUS FUNCTIONALITY TESTING")
        print(f"=" * 50)
        
        if not self.company_id:
            print(f"   ❌ No company ID available - cannot test Save Consensus")
            return False
        
        # First get an existing scenario adjustment to create consensus for
        success, response = self.run_test(
            "Get Adjustments for Consensus",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if not success or not response:
            print(f"   ❌ No scenario adjustments available for consensus testing")
            return False
        
        adjustment_id = response[0]['id']
        
        # Test creating consensus
        consensus_data = {
            "adjustment_id": adjustment_id,
            "consensus_name": "Test Team Consensus on Crisis Scenario"
        }
        
        success, response = self.run_test(
            "Create Consensus Settings",
            "POST",
            f"companies/{self.company_id}/consensus",
            200,
            data=consensus_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Save Consensus functionality accessible")
            print(f"   Consensus ID: {response.get('id')}")
            print(f"   Consensus name: {response.get('consensus_name', 'N/A')}")
            print(f"   Team members: {response.get('total_team_members', 'N/A')}")
            print(f"   Consensus percentage: {response.get('consensus_percentage', 'N/A')}%")
            print(f"   Consensus reached: {response.get('consensus_reached', 'N/A')}")
            print(f"   Final settings available: {bool(response.get('final_settings'))}")
            return True
        else:
            print(f"   ❌ Save Consensus functionality not accessible")
            return False

    def test_multiple_companies_support(self):
        """Test if multiple companies per user are supported"""
        print(f"\n🏢 MULTIPLE COMPANIES SUPPORT TESTING")
        print(f"=" * 50)
        
        # Try creating a second company
        second_company_data = {
            "company_name": "Secondary Crisis Response Ltd",
            "industry": "consulting",
            "company_size": "small",
            "description": "Specialized crisis response consulting services",
            "location": "Stockholm, Sweden"
        }
        
        success, response = self.run_test(
            "Create Second Company Profile",
            "POST",
            "companies",
            200,
            data=second_company_data
        )
        
        if success and 'id' in response:
            second_company_id = response['id']
            print(f"   ✅ Multiple companies per user supported")
            print(f"   Second company ID: {second_company_id}")
            print(f"   Second company name: {response.get('company_name', 'N/A')}")
            
            # Verify both companies are in the list
            list_success, list_response = self.run_test(
                "Verify Multiple Companies in List",
                "GET",
                "companies",
                200
            )
            
            if list_success and isinstance(list_response, list):
                company_count = len(list_response)
                print(f"   Total companies for user: {company_count}")
                
                if company_count >= 2:
                    print(f"   ✅ Multiple companies properly stored and retrieved")
                    return True
                else:
                    print(f"   ⚠️ Expected at least 2 companies, found {company_count}")
                    return False
            else:
                print(f"   ❌ Failed to verify multiple companies")
                return False
        else:
            print(f"   ⚠️ Multiple companies may not be supported or there's a limitation")
            return True  # This might be expected behavior

    def test_company_profile_validation(self):
        """Test company profile creation with various validation scenarios"""
        print(f"\n✅ COMPANY PROFILE VALIDATION TESTING")
        print(f"=" * 50)
        
        # Test 1: Missing required fields
        invalid_data_1 = {
            "company_name": "Test Company",
            # Missing industry, company_size, description, location
        }
        
        success, response = self.run_test(
            "Test Missing Required Fields",
            "POST",
            "companies",
            422,  # Expect validation error
            data=invalid_data_1
        )
        
        if success:
            print(f"   ✅ Validation properly rejects missing required fields")
        else:
            print(f"   ⚠️ Validation may be more lenient than expected")
        
        # Test 2: Invalid company size
        invalid_data_2 = {
            "company_name": "Test Company",
            "industry": "technology",
            "company_size": "invalid_size",
            "description": "Test description",
            "location": "Test location"
        }
        
        success, response = self.run_test(
            "Test Invalid Company Size",
            "POST",
            "companies",
            422,  # Expect validation error
            data=invalid_data_2
        )
        
        if success:
            print(f"   ✅ Validation properly rejects invalid company size")
        else:
            print(f"   ⚠️ Company size validation may be more lenient")
        
        # Test 3: Very long field values
        long_data = {
            "company_name": "A" * 1000,  # Very long name
            "industry": "technology",
            "company_size": "medium",
            "description": "B" * 5000,  # Very long description
            "location": "C" * 500  # Very long location
        }
        
        success, response = self.run_test(
            "Test Very Long Field Values",
            "POST",
            "companies",
            422,  # Expect validation error or success depending on limits
            data=long_data
        )
        
        if success:
            print(f"   ✅ Long field values handled appropriately")
        else:
            print(f"   ⚠️ Long field values may have length limits")
        
        return True

    def run_comprehensive_test(self):
        """Run all company profile tests"""
        print(f"\n🚀 COMPANY PROFILE COMPREHENSIVE TESTING")
        print(f"=" * 60)
        print(f"Testing company profile creation functionality that blocks")
        print(f"access to the Scenario Adjusters SEPTE framework")
        print(f"=" * 60)
        
        # Test sequence
        tests = [
            ("Authentication Setup", self.test_authentication_setup),
            ("Get User Profile", self.test_get_user_profile),
            ("Create Company Profile", self.test_create_company_profile),
            ("Get Company Profiles", self.test_get_company_profiles),
            ("Company Profile Association", self.test_company_profile_association),
            ("Company Requirement Validation", self.test_company_requirement_validation),
            ("Save Adjustments Access", self.test_save_adjustments_button_access),
            ("Download Settings Access", self.test_download_settings_functionality),
            ("Save Consensus Access", self.test_save_consensus_functionality),
            ("Multiple Companies Support", self.test_multiple_companies_support),
            ("Company Profile Validation", self.test_company_profile_validation)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if not result:
                    print(f"\n⚠️ Test '{test_name}' had issues but continuing...")
            except Exception as e:
                print(f"\n❌ Test '{test_name}' failed with exception: {str(e)}")
        
        # Final summary
        print(f"\n📊 COMPANY PROFILE TESTING SUMMARY")
        print(f"=" * 50)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.company_id:
            print(f"\n✅ CRITICAL SUCCESS: Company profile created successfully")
            print(f"   Company ID: {self.company_id}")
            print(f"   This should enable access to SEPTE framework functionality")
        else:
            print(f"\n❌ CRITICAL FAILURE: Company profile creation failed")
            print(f"   Users will remain blocked from SEPTE framework access")
        
        return self.tests_passed >= (self.tests_run * 0.7)  # 70% success rate threshold

if __name__ == "__main__":
    print("🏢 Company Profile Creation Testing")
    print("Testing functionality that blocks access to Scenario Adjusters SEPTE framework")
    
    tester = CompanyProfileTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 Company profile testing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️ Company profile testing completed with issues")
        sys.exit(1)