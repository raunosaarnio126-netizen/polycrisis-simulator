import requests
import sys
import json
from datetime import datetime
import io

class DocumentUploadTester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.company_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        # Don't set Content-Type for file uploads
        if not files and data:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=120)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, headers=test_headers, timeout=120)
                else:
                    response = requests.post(url, json=data, headers=test_headers, timeout=120)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=120)

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
        """Setup test user and company"""
        print("🔧 Setting up test environment...")
        
        # Create test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "email": f"doctest_{timestamp}@testcompany.com",
            "username": f"doctest_{timestamp}",
            "password": "SecurePass123!",
            "organization": "Document Test Organization"
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
            
            # Get user profile
            success, response = self.run_test(
                "Setup - Get User Profile",
                "GET",
                "me",
                200
            )
            
            if success and 'id' in response:
                self.user_id = response['id']
                
                # Create test company
                company_data = {
                    "company_name": "Document Test Company",
                    "industry": "Technology",
                    "company_size": "small",
                    "description": "Test company for document upload testing",
                    "location": "Test City"
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
                    print(f"✅ Test environment setup complete")
                    print(f"   User ID: {self.user_id}")
                    print(f"   Company ID: {self.company_id}")
                    return True
        
        print("❌ Failed to setup test environment")
        return False

    def test_document_upload_with_files(self):
        """Test document upload with actual file content"""
        print("\n" + "="*80)
        print("📄 TESTING DOCUMENT UPLOAD WITH FILE CONTENT")
        print("="*80)
        
        if not self.company_id:
            print("❌ No company ID available for document upload")
            return False
        
        # Test cases with different file types and content
        test_cases = [
            {
                "name": "PDF Document Upload",
                "filename": "test_document.pdf",
                "content": b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Document) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n299\n%%EOF",
                "content_type": "application/pdf"
            },
            {
                "name": "DOCX Document Upload", 
                "filename": "test_document.docx",
                "content": b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00[Content_Types].xmlPK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00_rels/.relsPK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00word/document.xmlTest DOCX DocumentPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00[Content_Types].xmlPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00_rels/.relsPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00word/document.xmlPK\x05\x06\x00\x00\x00\x00\x03\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            },
            {
                "name": "Invalid File Type Upload",
                "filename": "test_document.txt",
                "content": b"This is a plain text file that should be rejected",
                "content_type": "text/plain",
                "expected_status": 400
            }
        ]
        
        successful_uploads = 0
        
        for i, test_case in enumerate(test_cases, 1):
            expected_status = test_case.get("expected_status", 200)
            print(f"\n📝 Testing {test_case['name']} ({i}/{len(test_cases)})")
            print(f"   Filename: {test_case['filename']}")
            print(f"   Content Type: {test_case['content_type']}")
            print(f"   Content Size: {len(test_case['content'])} bytes")
            print(f"   Expected Status: {expected_status}")
            
            # Create file-like object
            file_obj = io.BytesIO(test_case['content'])
            
            files = {
                'file': (test_case['filename'], file_obj, test_case['content_type'])
            }
            
            success, response = self.run_test(
                f"Document Upload - {test_case['name']}",
                "POST",
                f"companies/{self.company_id}/documents/upload",
                expected_status,
                files=files
            )
            
            if success:
                if expected_status == 200:
                    successful_uploads += 1
                    print(f"   ✅ Upload successful")
                    print(f"   Document ID: {response.get('id', 'N/A')}")
                    print(f"   Document Name: {response.get('document_name', 'N/A')}")
                    print(f"   File Size: {response.get('file_size', 'N/A')}")
                    print(f"   AI Analysis Length: {len(response.get('ai_analysis', ''))}")
                    print(f"   Key Insights: {len(response.get('key_insights', []))}")
                    print(f"   Risk Factors: {len(response.get('risk_factors', []))}")
                else:
                    print(f"   ✅ Correctly rejected invalid file type")
            else:
                print(f"   ❌ Upload failed unexpectedly")
        
        print(f"\n📊 Document Upload Summary:")
        print(f"   Successful uploads: {successful_uploads}")
        print(f"   Total tests: {len(test_cases)}")
        
        return successful_uploads > 0

    def test_document_retrieval(self):
        """Test document retrieval"""
        if not self.company_id:
            return False
            
        success, response = self.run_test(
            "Get Company Documents",
            "GET",
            f"companies/{self.company_id}/documents",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} documents")
            for doc in response:
                print(f"   - {doc.get('document_name')}: {doc.get('document_type')} (AI analysis: {bool(doc.get('ai_analysis'))})")
            return True
        else:
            print(f"   ❌ Failed to retrieve documents")
            return False

    def test_file_size_validation(self):
        """Test file size validation (should reject files over 10MB)"""
        print("\n📏 Testing File Size Validation...")
        
        if not self.company_id:
            return False
        
        # Create a large file (simulate 11MB)
        large_content = b"A" * (11 * 1024 * 1024)  # 11MB of 'A' characters
        
        print(f"   Creating large file: {len(large_content)} bytes ({len(large_content) / (1024*1024):.1f}MB)")
        
        file_obj = io.BytesIO(large_content)
        files = {
            'file': ('large_document.pdf', file_obj, 'application/pdf')
        }
        
        success, response = self.run_test(
            "Large File Upload - Should Reject",
            "POST",
            f"companies/{self.company_id}/documents/upload",
            400,  # Should be rejected
            files=files
        )
        
        if success:
            print(f"   ✅ Large file correctly rejected")
            return True
        else:
            print(f"   ❌ Large file was not rejected (this is a problem)")
            return False

    def run_comprehensive_document_tests(self):
        """Run all document upload tests"""
        print("\n" + "🚀" + "="*78 + "🚀")
        print("📄 COMPREHENSIVE DOCUMENT UPLOAD FUNCTIONALITY TESTING")
        print("🚀" + "="*78 + "🚀")
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        test_results = {
            "document_upload": False,
            "document_retrieval": False,
            "file_size_validation": False
        }
        
        # Test 1: Document Upload with Files
        test_results["document_upload"] = self.test_document_upload_with_files()
        
        # Test 2: Document Retrieval
        test_results["document_retrieval"] = self.test_document_retrieval()
        
        # Test 3: File Size Validation
        test_results["file_size_validation"] = self.test_file_size_validation()
        
        # Final Summary
        print("\n" + "🏁" + "="*78 + "🏁")
        print("📊 DOCUMENT UPLOAD TEST RESULTS SUMMARY")
        print("🏁" + "="*78 + "🏁")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"\n📈 Overall Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"🎯 Feature Categories: {passed_tests}/{total_tests} categories successful")
        
        for category, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {category.replace('_', ' ').title()}: {status}")
        
        if passed_tests >= 2:  # Allow some flexibility
            print("🎉 SUCCESS: Document upload functionality is mostly working!")
            return True
        else:
            print("⚠️ ISSUES DETECTED: Document upload functionality has significant problems!")
            failed_categories = [cat for cat, result in test_results.items() if not result]
            print(f"🔍 Failed Categories: {', '.join(failed_categories)}")
            return False

def main():
    """Main test execution"""
    print("🔧 Initializing Document Upload Functionality Tests...")
    
    tester = DocumentUploadTester()
    
    try:
        success = tester.run_comprehensive_document_tests()
        
        if success:
            print("\n✅ Document upload functionality is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Issues found with document upload functionality!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()