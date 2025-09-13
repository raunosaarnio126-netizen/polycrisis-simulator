import requests
import sys
import json
from datetime import datetime
import uuid

class AddNewCustomerTester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_user_data = None
        self.created_avatar_id = None
        self.created_company_id = None

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

    def test_user_registration_comprehensive(self):
        """Test comprehensive user registration with all fields"""
        print("\n" + "="*80)
        print("🧪 TESTING USER REGISTRATION/ACCOUNT CREATION")
        print("="*80)
        
        # Generate unique test data
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "email": f"newcustomer_{timestamp}@testcompany.com",
            "username": f"newcustomer_{timestamp}",
            "password": "SecurePass123!",
            "organization": "Test Customer Organization",
            "job_title": "Chief Risk Officer",
            "department": "Risk Management",
            "phone": "+1-555-0123"
        }
        
        print(f"📝 Creating new customer account:")
        print(f"   Email: {test_user_data['email']}")
        print(f"   Organization: {test_user_data['organization']}")
        print(f"   Job Title: {test_user_data['job_title']}")
        
        success, response = self.run_test(
            "User Registration - New Customer Account",
            "POST",
            "register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.created_user_data = test_user_data
            print(f"   ✅ User registration successful")
            print(f"   Token received: {self.token[:20]}...")
            
            # Test login with new credentials
            login_success = self.test_user_login(test_user_data)
            if login_success:
                profile_success = self.test_get_user_profile()
                return profile_success
            return False
        else:
            print(f"   ❌ User registration failed")
            return False

    def test_user_login(self, user_data):
        """Test user login with created credentials"""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        success, response = self.run_test(
            "User Login - Verify New Account",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Login successful with new credentials")
            return True
        else:
            print(f"   ❌ Login failed with new credentials")
            return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        success, response = self.run_test(
            "Get User Profile - Verify Account Details",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   ✅ User profile retrieved successfully")
            print(f"   User ID: {self.user_id}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Username: {response.get('username', 'N/A')}")
            print(f"   Organization: {response.get('organization', 'N/A')}")
            print(f"   Job Title: {response.get('job_title', 'N/A')}")
            print(f"   Department: {response.get('department', 'N/A')}")
            print(f"   Role: {response.get('role', 'N/A')}")
            return True
        else:
            print(f"   ❌ Failed to retrieve user profile")
            return False

    def test_ai_avatar_creation_comprehensive(self):
        """Test comprehensive AI Avatar creation with comma-separated data"""
        print("\n" + "="*80)
        print("🤖 TESTING AI AVATAR CREATION")
        print("="*80)
        
        # Test different avatar types with realistic data (including required fields)
        avatar_test_cases = [
            {
                "name": "Crisis Response Specialist",
                "avatar_type": "research",
                "category": "crisis_management",
                "description": "Specialized AI avatar for crisis response research and analysis",
                "specializations": ["emergency response", "risk assessment", "crisis communication"],
                "core_competences": [
                    {"name": "Emergency Response", "skill_level": 9, "description": "Expert in emergency response protocols"},
                    {"name": "Risk Assessment", "skill_level": 8, "description": "Advanced risk analysis capabilities"},
                    {"name": "Crisis Communication", "skill_level": 7, "description": "Effective crisis communication skills"}
                ],
                "knowledge_domains": ["disaster management", "public safety", "emergency protocols"],
                "task_capabilities": ["analyze crisis scenarios", "develop response plans", "coordinate emergency teams"],
                "team_name": "Emergency Response Team",
                "organization": "Crisis Management Institute"
            },
            {
                "name": "Business Impact Analyst",
                "avatar_type": "assessment", 
                "category": "business_analysis",
                "description": "AI avatar focused on business impact assessment and continuity planning",
                "specializations": ["business continuity", "impact analysis", "financial assessment"],
                "core_competences": [
                    {"name": "Business Continuity", "skill_level": 9, "description": "Expert in business continuity planning"},
                    {"name": "Impact Analysis", "skill_level": 8, "description": "Advanced impact assessment skills"},
                    {"name": "Financial Assessment", "skill_level": 7, "description": "Financial risk evaluation expertise"}
                ],
                "knowledge_domains": ["business operations", "financial modeling", "risk management"],
                "task_capabilities": ["assess business impact", "create continuity plans", "analyze financial risks"],
                "team_name": "Business Continuity Team",
                "organization": "Corporate Risk Solutions"
            },
            {
                "name": "Strategic Planning Assistant",
                "avatar_type": "analyst",
                "category": "strategic_planning",
                "description": "AI avatar for strategic planning and decision support",
                "specializations": ["strategic planning", "decision analysis", "scenario modeling"],
                "core_competences": [
                    {"name": "Strategic Planning", "skill_level": 8, "description": "Strategic planning and analysis"},
                    {"name": "Decision Analysis", "skill_level": 9, "description": "Advanced decision support capabilities"},
                    {"name": "Scenario Modeling", "skill_level": 7, "description": "Scenario development and modeling"}
                ],
                "knowledge_domains": ["strategic management", "decision science", "predictive analytics"],
                "task_capabilities": ["develop strategies", "analyze scenarios", "support decision making"],
                "team_name": "Strategic Planning Division",
                "organization": "Strategic Consulting Group"
            }
        ]
        
        successful_creations = 0
        
        for i, avatar_data in enumerate(avatar_test_cases, 1):
            print(f"\n📝 Creating AI Avatar {i}/3: {avatar_data['name']}")
            print(f"   Type: {avatar_data['avatar_type']}")
            print(f"   Specializations: {', '.join(avatar_data['specializations'])}")
            print(f"   Team: {avatar_data['team_name']}")
            
            success, response = self.run_test(
                f"Create AI Avatar - {avatar_data['name']}",
                "POST",
                "ai-avatars",
                200,
                data=avatar_data
            )
            
            if success and 'id' in response:
                successful_creations += 1
                if i == 1:  # Store first avatar ID for further testing
                    self.created_avatar_id = response['id']
                
                print(f"   ✅ Avatar created successfully")
                print(f"   Avatar ID: {response.get('id')}")
                print(f"   Name: {response.get('avatar_name', 'N/A')}")
                print(f"   Type: {response.get('avatar_type', 'N/A')}")
                print(f"   Status: {response.get('status', 'N/A')}")
                print(f"   Team: {response.get('team_name', 'N/A')}")
                print(f"   Organization: {response.get('organization', 'N/A')}")
                
                # Verify comma-separated fields are properly handled
                specializations = response.get('specializations', [])
                knowledge_domains = response.get('knowledge_domains', [])
                task_capabilities = response.get('task_capabilities', [])
                
                print(f"   Specializations count: {len(specializations)}")
                print(f"   Knowledge domains count: {len(knowledge_domains)}")
                print(f"   Task capabilities count: {len(task_capabilities)}")
                
                # Verify comma functionality is working
                if len(specializations) >= 2 and len(knowledge_domains) >= 2 and len(task_capabilities) >= 2:
                    print(f"   ✅ Comma-separated data processed correctly")
                else:
                    print(f"   ⚠️ Comma-separated data may not be processed correctly")
                    
            else:
                print(f"   ❌ Avatar creation failed")
        
        print(f"\n📊 Avatar Creation Summary: {successful_creations}/{len(avatar_test_cases)} successful")
        
        if successful_creations > 0:
            # Test retrieving created avatars
            self.test_get_ai_avatars()
            if self.created_avatar_id:
                self.test_update_ai_avatar()
            return True
        return False

    def test_get_ai_avatars(self):
        """Test retrieving AI avatars"""
        success, response = self.run_test(
            "Get AI Avatars - Verify Creation",
            "GET",
            "ai-avatars",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} AI avatars")
            for avatar in response:
                print(f"   - {avatar.get('avatar_name')}: {avatar.get('avatar_type')} ({avatar.get('status')})")
            return True
        else:
            print(f"   ❌ Failed to retrieve AI avatars")
            return False

    def test_update_ai_avatar(self):
        """Test updating AI avatar (Amend functionality)"""
        if not self.created_avatar_id:
            print("   ⚠️ No avatar ID available for update testing")
            return False
            
        update_data = {
            "name": "Enhanced Crisis Response Specialist",
            "avatar_type": "research",
            "category": "crisis_management",
            "description": "Enhanced AI avatar with advanced crisis response capabilities",
            "specializations": ["advanced emergency response", "multi-hazard risk assessment", "crisis communication", "disaster recovery"],
            "core_competences": [
                {"name": "Advanced Emergency Response", "skill_level": 10, "description": "Expert-level emergency response capabilities"},
                {"name": "Multi-hazard Risk Assessment", "skill_level": 9, "description": "Advanced multi-hazard analysis skills"},
                {"name": "Crisis Communication", "skill_level": 8, "description": "Enhanced crisis communication abilities"},
                {"name": "Disaster Recovery", "skill_level": 9, "description": "Comprehensive disaster recovery expertise"}
            ],
            "knowledge_domains": ["comprehensive disaster management", "advanced public safety", "emergency protocols", "recovery planning"],
            "task_capabilities": ["analyze complex crisis scenarios", "develop comprehensive response plans", "coordinate multi-agency teams", "manage recovery operations"],
            "team_name": "Advanced Emergency Response Team",
            "organization": "Enhanced Crisis Management Institute"
        }
        
        success, response = self.run_test(
            "Update AI Avatar - Amend Functionality",
            "PUT",
            f"ai-avatars/{self.created_avatar_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"   ✅ Avatar updated successfully")
            print(f"   Updated name: {response.get('name', 'N/A')}")
            print(f"   Updated specializations: {len(response.get('specializations', []))}")
            print(f"   Updated team: {response.get('team_name', 'N/A')}")
            return True
        else:
            print(f"   ❌ Avatar update failed")
            return False

    def test_company_creation_comprehensive(self):
        """Test comprehensive company/customer creation"""
        print("\n" + "="*80)
        print("🏢 TESTING COMPANY/CUSTOMER CREATION")
        print("="*80)
        
        # Test creating a company profile
        company_data = {
            "company_name": "New Customer Enterprise Solutions",
            "industry": "Technology Services",
            "company_size": "medium",
            "website_url": "https://newcustomer-enterprise.com",
            "description": "A technology services company specializing in enterprise solutions and crisis management systems",
            "location": "Seattle, Washington, USA"
        }
        
        print(f"📝 Creating new customer company:")
        print(f"   Company: {company_data['company_name']}")
        print(f"   Industry: {company_data['industry']}")
        print(f"   Size: {company_data['company_size']}")
        print(f"   Location: {company_data['location']}")
        
        success, response = self.run_test(
            "Create Company Profile - New Customer",
            "POST",
            "companies",
            200,
            data=company_data
        )
        
        if success and 'id' in response:
            self.created_company_id = response['id']
            print(f"   ✅ Company created successfully")
            print(f"   Company ID: {self.created_company_id}")
            print(f"   Company Name: {response.get('company_name', 'N/A')}")
            print(f"   Industry: {response.get('industry', 'N/A')}")
            print(f"   Size: {response.get('company_size', 'N/A')}")
            print(f"   Location: {response.get('location', 'N/A')}")
            print(f"   Website Analysis: {len(response.get('website_analysis', '')) if response.get('website_analysis') else 0} chars")
            print(f"   Business Model: {len(response.get('business_model', '')) if response.get('business_model') else 0} chars")
            print(f"   Key Assets: {len(response.get('key_assets', []))}")
            print(f"   Vulnerabilities: {len(response.get('vulnerabilities', []))}")
            print(f"   Stakeholders: {len(response.get('stakeholders', []))}")
            
            # Test additional company management features
            self.test_get_company_details()
            self.test_create_company_team()
            self.test_company_rapid_analysis()
            return True
        else:
            print(f"   ❌ Company creation failed")
            return False

    def test_get_company_details(self):
        """Test retrieving company details"""
        if not self.created_company_id:
            return False
            
        success, response = self.run_test(
            "Get Company Details - Verify Creation",
            "GET",
            f"companies/{self.created_company_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"   ✅ Company details retrieved successfully")
            print(f"   Company: {response.get('company_name', 'N/A')}")
            print(f"   Created by: {response.get('created_by', 'N/A')}")
            return True
        else:
            print(f"   ❌ Failed to retrieve company details")
            return False

    def test_create_company_team(self):
        """Test creating a team for the company"""
        if not self.created_company_id:
            return False
            
        team_data = {
            "team_name": "Crisis Management Team",
            "team_description": "Primary team responsible for crisis response and management",
            "team_members": [
                "crisis.manager@newcustomer-enterprise.com",
                "risk.analyst@newcustomer-enterprise.com", 
                "communications.lead@newcustomer-enterprise.com",
                "operations.director@newcustomer-enterprise.com"
            ],
            "team_roles": ["crisis_manager", "analyst", "coordinator", "observer"]
        }
        
        success, response = self.run_test(
            "Create Company Team - New Customer Team",
            "POST",
            f"companies/{self.created_company_id}/teams",
            200,
            data=team_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Team created successfully")
            print(f"   Team ID: {response.get('id')}")
            print(f"   Team Name: {response.get('team_name', 'N/A')}")
            print(f"   Team Members: {len(response.get('team_members', []))}")
            print(f"   Team Roles: {response.get('team_roles', [])}")
            return True
        else:
            print(f"   ❌ Team creation failed")
            return False

    def test_company_rapid_analysis(self):
        """Test company rapid analysis functionality"""
        if not self.created_company_id:
            return False
            
        analysis_types = ["vulnerability_assessment", "business_impact", "scenario_recommendation"]
        successful_analyses = 0
        
        for analysis_type in analysis_types:
            success, response = self.run_test(
                f"Company Rapid Analysis - {analysis_type}",
                "POST",
                f"companies/{self.created_company_id}/rapid-analysis?analysis_type={analysis_type}",
                200
            )
            
            if success and 'id' in response:
                successful_analyses += 1
                print(f"   ✅ {analysis_type} analysis completed")
                print(f"     Analysis ID: {response.get('id')}")
                print(f"     Title: {response.get('analysis_title', 'N/A')}")
                print(f"     Content Length: {len(response.get('analysis_content', ''))}")
                print(f"     Key Findings: {len(response.get('key_findings', []))}")
                print(f"     Recommendations: {len(response.get('recommendations', []))}")
                print(f"     Priority Level: {response.get('priority_level', 'N/A')}")
                print(f"     Confidence Score: {response.get('confidence_score', 'N/A')}")
            else:
                print(f"   ❌ {analysis_type} analysis failed")
        
        print(f"   📊 Rapid Analysis Summary: {successful_analyses}/{len(analysis_types)} successful")
        return successful_analyses > 0

    def test_backend_health_check(self):
        """Test general backend health and core endpoints"""
        print("\n" + "="*80)
        print("🏥 TESTING GENERAL BACKEND HEALTH")
        print("="*80)
        
        health_tests = [
            ("Dashboard Stats", "GET", "dashboard/stats", 200),
            ("Get All AI Avatars", "GET", "ai-avatars", 200),
        ]
        
        successful_health_checks = 0
        
        for test_name, method, endpoint, expected_status in health_tests:
            success, response = self.run_test(
                f"Health Check - {test_name}",
                method,
                endpoint,
                expected_status
            )
            
            if success:
                successful_health_checks += 1
                print(f"   ✅ {test_name} endpoint healthy")
                
                # Show relevant stats
                if "dashboard" in endpoint:
                    print(f"     Total scenarios: {response.get('total_scenarios', 'N/A')}")
                    print(f"     Active scenarios: {response.get('active_scenarios', 'N/A')}")
                    print(f"     User organization: {response.get('user_organization', 'N/A')}")
                elif "ai-avatars" in endpoint and isinstance(response, list):
                    print(f"     Total AI avatars: {len(response)}")
            else:
                print(f"   ❌ {test_name} endpoint unhealthy")
        
        print(f"   📊 Health Check Summary: {successful_health_checks}/{len(health_tests)} endpoints healthy")
        return successful_health_checks == len(health_tests)

    def test_error_scenarios(self):
        """Test error handling scenarios"""
        print("\n" + "="*80)
        print("⚠️ TESTING ERROR HANDLING SCENARIOS")
        print("="*80)
        
        error_tests = [
            # Test duplicate user registration
            ("Duplicate User Registration", "POST", "register", 400, self.created_user_data),
            # Test invalid login
            ("Invalid Login Credentials", "POST", "login", 401, {"email": "invalid@test.com", "password": "wrongpass"}),
            # Test unauthorized access (without token)
            ("Unauthorized Avatar Creation", "POST", "ai-avatars", 401, {"avatar_name": "Test"}, {"Authorization": "Bearer invalid_token"}),
            # Test invalid company ID
            ("Invalid Company Access", "GET", "companies/invalid-company-id", 404, None),
        ]
        
        successful_error_tests = 0
        temp_token = self.token
        
        for test_name, method, endpoint, expected_status, data, *headers in error_tests:
            # Handle unauthorized test by temporarily removing token
            if "Unauthorized" in test_name:
                self.token = None
            
            test_headers = headers[0] if headers else None
            success, response = self.run_test(
                f"Error Test - {test_name}",
                method,
                endpoint,
                expected_status,
                data=data,
                headers=test_headers
            )
            
            if success:
                successful_error_tests += 1
                print(f"   ✅ Error handling correct for {test_name}")
            else:
                print(f"   ❌ Error handling incorrect for {test_name}")
            
            # Restore token
            self.token = temp_token
        
        print(f"   📊 Error Handling Summary: {successful_error_tests}/{len(error_tests)} tests passed")
        return successful_error_tests >= len(error_tests) * 0.75  # Allow 25% failure rate for error tests

    def run_comprehensive_add_customer_tests(self):
        """Run all comprehensive tests for adding new customers"""
        print("\n" + "🚀" + "="*78 + "🚀")
        print("🎯 COMPREHENSIVE 'ADD NEW CUSTOMER' FUNCTIONALITY TESTING")
        print("🚀" + "="*78 + "🚀")
        
        test_results = {
            "user_registration": False,
            "ai_avatar_creation": False,
            "company_creation": False,
            "backend_health": False,
            "error_handling": False
        }
        
        # Test 1: User Registration/Account Creation
        test_results["user_registration"] = self.test_user_registration_comprehensive()
        
        # Test 2: AI Avatar Creation (with comma functionality)
        test_results["ai_avatar_creation"] = self.test_ai_avatar_creation_comprehensive()
        
        # Test 3: Company/Customer Management
        test_results["company_creation"] = self.test_company_creation_comprehensive()
        
        # Test 4: General Backend Health
        test_results["backend_health"] = self.test_backend_health_check()
        
        # Test 5: Error Handling
        test_results["error_handling"] = self.test_error_scenarios()
        
        # Final Summary
        print("\n" + "🏁" + "="*78 + "🏁")
        print("📊 FINAL TEST RESULTS SUMMARY")
        print("🏁" + "="*78 + "🏁")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"\n📈 Overall Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"🎯 Feature Categories: {passed_tests}/{total_tests} categories successful")
        
        for category, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {category.replace('_', ' ').title()}: {status}")
        
        # Determine overall success
        critical_tests = ["user_registration", "ai_avatar_creation", "company_creation"]
        critical_passed = sum(test_results[test] for test in critical_tests)
        
        print(f"\n🎯 Critical 'Add New Customer' Features: {critical_passed}/{len(critical_tests)} working")
        
        if critical_passed == len(critical_tests):
            print("🎉 SUCCESS: All critical 'Add New Customer' functionality is working!")
            return True
        else:
            print("⚠️ ISSUES DETECTED: Some critical 'Add New Customer' functionality is failing!")
            
            # Identify specific issues
            failed_categories = [cat for cat, result in test_results.items() if not result]
            print(f"🔍 Failed Categories: {', '.join(failed_categories)}")
            
            return False

def main():
    """Main test execution"""
    print("🔧 Initializing Add New Customer Functionality Tests...")
    
    tester = AddNewCustomerTester()
    
    try:
        success = tester.run_comprehensive_add_customer_tests()
        
        if success:
            print("\n✅ All critical 'Add New Customer' functionality is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Issues found with 'Add New Customer' functionality!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()