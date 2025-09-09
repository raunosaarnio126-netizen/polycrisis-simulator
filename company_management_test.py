import requests
import sys
import json
from datetime import datetime

class CompanyManagementTester:
    def __init__(self, base_url="https://crisis-monitor-3.preview.emergentagent.com"):
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

    def setup_test_environment(self):
        """Setup test user and company"""
        # Register test user
        test_user_data = {
            "email": f"company_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"companytest_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Test Company Management Org",
            "job_title": "Crisis Management Director",
            "department": "Risk Management"
        }
        
        success, response = self.run_test(
            "Setup - User Registration",
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
            "Setup - Get User Profile",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
        else:
            return False
            
        # Create test company
        company_data = {
            "company_name": "Test Company Management Corp",
            "industry": "Technology",
            "company_size": "medium",
            "website_url": "https://testcompany.example.com",
            "description": "A test company for crisis management simulation and document analysis",
            "location": "San Francisco, CA"
        }
        
        success, response = self.run_test(
            "Setup - Create Company",
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

    def test_document_upload_pdf(self):
        """Test PDF Document Upload with AI Analysis"""
        if not self.company_id:
            print("❌ No company ID available")
            return False
            
        # Create a realistic PDF content for testing
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
72 720 Td
(BUSINESS CONTINUITY PLAN) Tj
0 -20 Td
(Executive Summary:) Tj
0 -15 Td
(This document outlines our crisis management strategy) Tj
0 -15 Td
(Key risks include cyber attacks, natural disasters) Tj
0 -15 Td
(Recovery procedures and emergency contacts included) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
450
%%EOF"""
        
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('business_continuity_plan.pdf', pdf_content, 'application/pdf')}
        data = {'document_type': 'business_plan'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing PDF Document Upload with AI Analysis...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - PDF uploaded and analyzed")
                
                response_data = response.json()
                print(f"   Document ID: {response_data.get('id', 'N/A')}")
                print(f"   Document name: {response_data.get('document_name', 'N/A')}")
                print(f"   AI analysis length: {len(response_data.get('ai_analysis', ''))}")
                print(f"   Key insights: {len(response_data.get('key_insights', []))}")
                print(f"   Risk factors: {len(response_data.get('risk_factors', []))}")
                print(f"   File size: {response_data.get('file_size', 'N/A')}")
                
                # Verify AI analysis was generated
                if not response_data.get('ai_analysis'):
                    print(f"   ⚠️ AI analysis is missing or empty")
                    return False
                    
                if len(response_data.get('key_insights', [])) == 0:
                    print(f"   ⚠️ Key insights are missing")
                    return False
                    
                if len(response_data.get('risk_factors', [])) == 0:
                    print(f"   ⚠️ Risk factors are missing")
                    return False
                
                print(f"   ✅ AI analysis generated successfully")
                return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_document_upload_docx(self):
        """Test DOCX Document Upload with AI Analysis"""
        if not self.company_id:
            print("❌ No company ID available")
            return False
            
        # Create a simple DOCX content for testing
        docx_content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00[Content_Types].xmlPK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00_rels/.relsPK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00word/document.xmlPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00[Content_Types].xmlPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01F\x00\x00\x00_rels/.relsPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x84\x00\x00\x00word/document.xmlPK\x05\x06\x00\x00\x00\x00\x03\x00\x03\x00\xca\x00\x00\x00\xd3\x00\x00\x00\x00\x00'
        
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('risk_assessment.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {'document_type': 'operational_plan'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing DOCX Document Upload with AI Analysis...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - DOCX uploaded and analyzed")
                
                response_data = response.json()
                print(f"   Document ID: {response_data.get('id', 'N/A')}")
                print(f"   Document name: {response_data.get('document_name', 'N/A')}")
                print(f"   AI analysis length: {len(response_data.get('ai_analysis', ''))}")
                print(f"   Key insights: {len(response_data.get('key_insights', []))}")
                print(f"   Risk factors: {len(response_data.get('risk_factors', []))}")
                
                # Verify AI analysis was generated
                if not response_data.get('ai_analysis'):
                    print(f"   ⚠️ AI analysis is missing or empty")
                    return False
                
                print(f"   ✅ AI analysis generated successfully")
                return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_file_type_validation(self):
        """Test File Type Validation - Should reject non-PDF/DOCX files"""
        if not self.company_id:
            print("❌ No company ID available")
            return False
            
        # Test with a text file (should be rejected)
        txt_content = b"This is a plain text file that should be rejected by the system"
        
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('invalid_document.txt', txt_content, 'text/plain')}
        data = {'document_type': 'other'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing File Type Validation...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            # Should return 400 for invalid file type
            if response.status_code == 400:
                self.tests_passed += 1
                print(f"✅ Passed - Invalid file type correctly rejected")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data.get('detail', 'N/A')}")
                except:
                    pass
                return True
            else:
                print(f"❌ Failed - Expected 400, got {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_get_company_users(self):
        """Test GET /api/companies/{company_id}/users endpoint"""
        if not self.company_id:
            print("❌ No company ID available")
            return False
            
        success, response = self.run_test(
            "Get Company Users",
            "GET",
            f"companies/{self.company_id}/users",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users for company")
            for user in response:
                print(f"   - {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
                print(f"     Role: {user.get('role', 'N/A')}, Department: {user.get('department', 'N/A')}")
                
                # Verify User model fields are present
                required_fields = ['id', 'email', 'username', 'organization']
                for field in required_fields:
                    if field not in user:
                        print(f"   ⚠️ Missing required User field: {field}")
                        return False
            return True
        return False

    def test_rapid_analysis_all_types(self):
        """Test Rapid Analysis with All Analysis Types"""
        if not self.company_id:
            print("❌ No company ID available")
            return False
            
        analysis_types = [
            "vulnerability_assessment",
            "business_impact", 
            "scenario_recommendation",
            "competitive_analysis"
        ]
        
        successful_analyses = 0
        
        for analysis_type in analysis_types:
            success, response = self.run_test(
                f"Rapid Analysis - {analysis_type}",
                "POST",
                f"companies/{self.company_id}/rapid-analysis?analysis_type={analysis_type}",
                200
            )
            
            if success and 'id' in response:
                successful_analyses += 1
                print(f"   ✅ {analysis_type} analysis generated")
                print(f"     Analysis ID: {response.get('id')}")
                print(f"     Title: {response.get('analysis_title', 'N/A')}")
                print(f"     Content length: {len(response.get('analysis_content', ''))}")
                print(f"     Key findings: {len(response.get('key_findings', []))}")
                print(f"     Recommendations: {len(response.get('recommendations', []))}")
                print(f"     Priority level: {response.get('priority_level', 'N/A')}")
                print(f"     Confidence score: {response.get('confidence_score', 'N/A')}")
                
                # Verify RapidAnalysis model fields are present
                required_fields = ['id', 'analysis_content', 'key_findings', 'recommendations']
                for field in required_fields:
                    if field not in response or not response[field]:
                        print(f"   ⚠️ Missing or empty required field: {field}")
                        return False
                        
            else:
                print(f"   ❌ Failed to generate {analysis_type} analysis")
        
        print(f"   Successfully generated {successful_analyses}/{len(analysis_types)} rapid analyses")
        return successful_analyses == len(analysis_types)

    def test_team_management(self):
        """Test Team Management Endpoints"""
        if not self.company_id:
            print("❌ No company ID available")
            return False
            
        # Test creating team with email list
        team_data = {
            "team_name": "Crisis Response Alpha Team",
            "team_description": "Primary crisis response team for enterprise operations",
            "team_members": [
                "crisis.manager@company.com", 
                "operations.lead@company.com", 
                "communications.director@company.com"
            ],
            "team_roles": ["crisis_manager", "analyst", "coordinator"]
        }
        
        success, response = self.run_test(
            "Create Team with Email List",
            "POST",
            f"companies/{self.company_id}/teams",
            200,
            data=team_data
        )
        
        if success and 'id' in response:
            team_id = response['id']
            print(f"   ✅ Team created with ID: {team_id}")
            print(f"   Team name: {response.get('team_name', 'N/A')}")
            print(f"   Team members: {len(response.get('team_members', []))}")
            print(f"   Team roles: {response.get('team_roles', [])}")
            
            # Test getting company teams
            teams_success, teams_response = self.run_test(
                "Get Company Teams",
                "GET",
                f"companies/{self.company_id}/teams",
                200
            )
            
            if teams_success and isinstance(teams_response, list):
                print(f"   ✅ Retrieved {len(teams_response)} teams")
                
                # Find our created team
                created_team = None
                for team in teams_response:
                    if team.get('id') == team_id:
                        created_team = team
                        break
                
                if created_team:
                    print(f"   ✅ Team found in company teams list")
                    return True
                else:
                    print(f"   ❌ Team not found in company teams list")
                    return False
            else:
                print(f"   ❌ Failed to retrieve company teams")
                return False
        else:
            print(f"   ❌ Failed to create team")
            return False

def main():
    print("🚀 Starting Company Management Endpoints Tests")
    print("=" * 60)
    
    tester = CompanyManagementTester()
    
    # Setup test environment
    print("\n📝 Setting up test environment...")
    if not tester.setup_test_environment():
        print("❌ Failed to setup test environment")
        return 1
    
    # Test document upload endpoints
    print("\n📄 Testing Document Upload Endpoints...")
    tester.test_document_upload_pdf()
    tester.test_document_upload_docx()
    tester.test_file_type_validation()
    
    # Test company users endpoint
    print("\n👥 Testing Company Users Endpoint...")
    tester.test_get_company_users()
    
    # Test rapid analysis enhancements
    print("\n⚡ Testing Enhanced Rapid Analysis...")
    tester.test_rapid_analysis_all_types()
    
    # Test team management
    print("\n👨‍💼 Testing Team Management...")
    tester.test_team_management()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Company Management tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())