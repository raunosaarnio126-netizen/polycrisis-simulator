#!/usr/bin/env python3
"""
Authentication System Testing for Polycrisis Simulator
Focus: Identify why login is not working - Critical Issue Investigation
"""

import requests
import sys
import json
import hashlib
import jwt
from datetime import datetime, timezone
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class AuthenticationTester:
    def __init__(self):
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # API Configuration
        self.base_url = "https://adapt-crisis-sim.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Database Configuration
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        
        # Test Results
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.test_results = []
        
        print(f"🔧 Authentication System Tester Initialized")
        print(f"   API URL: {self.api_url}")
        print(f"   MongoDB URL: {self.mongo_url}")
        print(f"   Database: {self.db_name}")

    def log_result(self, test_name, success, details, is_critical=False):
        """Log test result with details"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
            if is_critical:
                self.critical_issues.append(f"{test_name}: {details}")
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": is_critical
        }
        self.test_results.append(result)
        
        print(f"\n{status} {test_name}")
        print(f"   Details: {details}")
        
        return success

    def test_database_connectivity(self):
        """Test MongoDB database connectivity"""
        try:
            client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            client.server_info()  # Force connection
            db = client[self.db_name]
            
            # Test basic operations
            collections = db.list_collection_names()
            users_exist = 'users' in collections
            
            details = f"Connected successfully. Collections: {len(collections)}. Users collection exists: {users_exist}"
            return self.log_result("Database Connectivity", True, details)
            
        except Exception as e:
            details = f"Database connection failed: {str(e)}"
            return self.log_result("Database Connectivity", False, details, is_critical=True)

    def test_user_records_in_database(self):
        """Test if users exist in database and check their structure"""
        try:
            client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            db = client[self.db_name]
            users_collection = db.users
            
            # Count total users
            total_users = users_collection.count_documents({})
            
            # Check for admin user
            admin_user = users_collection.find_one({"email": "admin@test.com"})
            admin_exists = admin_user is not None
            
            # Check for test user
            test_user = users_collection.find_one({"email": "test@example.com"})
            test_exists = test_user is not None
            
            # Get sample user structure
            sample_user = users_collection.find_one({})
            user_fields = list(sample_user.keys()) if sample_user else []
            
            details = f"Total users: {total_users}. Admin user exists: {admin_exists}. Test user exists: {test_exists}. User fields: {user_fields}"
            
            if total_users == 0:
                return self.log_result("User Records Check", False, "No users found in database", is_critical=True)
            
            # Check if password field exists
            if sample_user and 'password' not in sample_user:
                return self.log_result("User Records Check", False, "Users missing password field", is_critical=True)
            
            return self.log_result("User Records Check", True, details)
            
        except Exception as e:
            details = f"Database user check failed: {str(e)}"
            return self.log_result("User Records Check", False, details, is_critical=True)

    def test_password_hashing_verification(self):
        """Test password hashing and verification"""
        try:
            client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            db = client[self.db_name]
            users_collection = db.users
            
            # Get admin user to check password hash
            admin_user = users_collection.find_one({"email": "admin@test.com"})
            test_user = users_collection.find_one({"email": "test@example.com"})
            
            issues = []
            
            if admin_user:
                admin_password_hash = admin_user.get('password', '')
                if not admin_password_hash:
                    issues.append("Admin user has no password hash")
                elif not admin_password_hash.startswith('$2b$'):
                    issues.append(f"Admin password hash format incorrect: {admin_password_hash[:20]}...")
                else:
                    issues.append("Admin password hash format looks correct (bcrypt)")
            else:
                issues.append("Admin user not found")
            
            if test_user:
                test_password_hash = test_user.get('password', '')
                if not test_password_hash:
                    issues.append("Test user has no password hash")
                elif not test_password_hash.startswith('$2b$'):
                    issues.append(f"Test password hash format incorrect: {test_password_hash[:20]}...")
                else:
                    issues.append("Test password hash format looks correct (bcrypt)")
            else:
                issues.append("Test user not found")
            
            details = "; ".join(issues)
            
            # Check if we have critical issues
            critical_issues = [issue for issue in issues if "not found" in issue or "no password" in issue or "incorrect" in issue]
            has_critical = len(critical_issues) > 0
            
            return self.log_result("Password Hash Verification", not has_critical, details, is_critical=has_critical)
            
        except Exception as e:
            details = f"Password hash verification failed: {str(e)}"
            return self.log_result("Password Hash Verification", False, details, is_critical=True)

    def test_registration_endpoint(self):
        """Test user registration endpoint"""
        try:
            # Create unique test user
            timestamp = datetime.now().strftime('%H%M%S')
            test_user_data = {
                "email": f"auth_test_{timestamp}@example.com",
                "username": f"authtest_{timestamp}",
                "password": "TestPass123!",
                "organization": "Auth Test Organization"
            }
            
            url = f"{self.api_url}/register"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=test_user_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data and 'token_type' in response_data:
                    # Verify token format
                    token = response_data['access_token']
                    token_parts = token.split('.')
                    
                    if len(token_parts) == 3:
                        details = f"Registration successful. Token format valid (JWT). Token length: {len(token)}"
                        self.test_registration_token = token
                        self.test_user_data = test_user_data
                        return self.log_result("Registration Endpoint", True, details)
                    else:
                        details = f"Registration successful but token format invalid: {token[:50]}..."
                        return self.log_result("Registration Endpoint", False, details, is_critical=True)
                else:
                    details = f"Registration response missing token fields: {response_data}"
                    return self.log_result("Registration Endpoint", False, details, is_critical=True)
            else:
                details = f"Registration failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Registration Endpoint", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Registration endpoint test failed: {str(e)}"
            return self.log_result("Registration Endpoint", False, details, is_critical=True)

    def test_login_with_admin_credentials(self):
        """Test login with admin@test.com / admin123"""
        try:
            login_data = {
                "email": "admin@test.com",
                "password": "admin123"
            }
            
            url = f"{self.api_url}/login"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=login_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"Admin login successful. Token received: {token[:50]}..."
                    self.admin_token = token
                    return self.log_result("Admin Login", True, details)
                else:
                    details = f"Admin login response missing token: {response_data}"
                    return self.log_result("Admin Login", False, details, is_critical=True)
            elif response.status_code == 401:
                details = f"Admin login failed - Invalid credentials (401). This is the CRITICAL ISSUE."
                return self.log_result("Admin Login", False, details, is_critical=True)
            else:
                details = f"Admin login failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Admin Login", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Admin login test failed: {str(e)}"
            return self.log_result("Admin Login", False, details, is_critical=True)

    def test_login_with_test_credentials(self):
        """Test login with test@example.com / password123"""
        try:
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            url = f"{self.api_url}/login"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=login_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"Test user login successful. Token received: {token[:50]}..."
                    self.test_token = token
                    return self.log_result("Test User Login", True, details)
                else:
                    details = f"Test user login response missing token: {response_data}"
                    return self.log_result("Test User Login", False, details, is_critical=True)
            elif response.status_code == 401:
                details = f"Test user login failed - Invalid credentials (401). This is a CRITICAL ISSUE."
                return self.log_result("Test User Login", False, details, is_critical=True)
            else:
                details = f"Test user login failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Test User Login", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Test user login test failed: {str(e)}"
            return self.log_result("Test User Login", False, details, is_critical=True)

    def test_login_with_new_user(self):
        """Test login with newly registered user"""
        if not hasattr(self, 'test_user_data'):
            details = "No test user data available from registration"
            return self.log_result("New User Login", False, details, is_critical=True)
        
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            url = f"{self.api_url}/login"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=login_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"New user login successful. Token received: {token[:50]}..."
                    return self.log_result("New User Login", True, details)
                else:
                    details = f"New user login response missing token: {response_data}"
                    return self.log_result("New User Login", False, details, is_critical=True)
            elif response.status_code == 401:
                details = f"New user login failed - Invalid credentials (401). Registration/Login cycle broken."
                return self.log_result("New User Login", False, details, is_critical=True)
            else:
                details = f"New user login failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("New User Login", False, details, is_critical=True)
                
        except Exception as e:
            details = f"New user login test failed: {str(e)}"
            return self.log_result("New User Login", False, details, is_critical=True)

    def test_jwt_token_validation(self):
        """Test JWT token validation and structure"""
        tokens_to_test = []
        
        if hasattr(self, 'admin_token'):
            tokens_to_test.append(("Admin", self.admin_token))
        if hasattr(self, 'test_token'):
            tokens_to_test.append(("Test User", self.test_token))
        if hasattr(self, 'test_registration_token'):
            tokens_to_test.append(("Registration", self.test_registration_token))
        
        if not tokens_to_test:
            details = "No tokens available for validation"
            return self.log_result("JWT Token Validation", False, details, is_critical=True)
        
        try:
            validation_results = []
            
            for token_name, token in tokens_to_test:
                # Decode without verification to check structure
                try:
                    # Split token to check format
                    parts = token.split('.')
                    if len(parts) != 3:
                        validation_results.append(f"{token_name}: Invalid JWT format")
                        continue
                    
                    # Decode header and payload (without verification)
                    import base64
                    import json
                    
                    # Add padding if needed
                    header_b64 = parts[0] + '=' * (4 - len(parts[0]) % 4)
                    payload_b64 = parts[1] + '=' * (4 - len(parts[1]) % 4)
                    
                    header = json.loads(base64.urlsafe_b64decode(header_b64))
                    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                    
                    # Check required fields
                    required_fields = ['sub', 'exp']
                    missing_fields = [field for field in required_fields if field not in payload]
                    
                    if missing_fields:
                        validation_results.append(f"{token_name}: Missing fields {missing_fields}")
                    else:
                        validation_results.append(f"{token_name}: Valid structure, user_id: {payload.get('sub', 'N/A')}")
                        
                except Exception as decode_error:
                    validation_results.append(f"{token_name}: Decode error - {str(decode_error)}")
            
            details = "; ".join(validation_results)
            
            # Check if any tokens had issues
            has_issues = any("error" in result.lower() or "invalid" in result.lower() or "missing" in result.lower() 
                           for result in validation_results)
            
            return self.log_result("JWT Token Validation", not has_issues, details, is_critical=has_issues)
            
        except Exception as e:
            details = f"JWT validation failed: {str(e)}"
            return self.log_result("JWT Token Validation", False, details, is_critical=True)

    def test_auth_me_endpoint(self):
        """Test /api/me endpoint with valid tokens"""
        tokens_to_test = []
        
        if hasattr(self, 'admin_token'):
            tokens_to_test.append(("Admin", self.admin_token))
        if hasattr(self, 'test_token'):
            tokens_to_test.append(("Test User", self.test_token))
        if hasattr(self, 'test_registration_token'):
            tokens_to_test.append(("Registration", self.test_registration_token))
        
        if not tokens_to_test:
            details = "No tokens available for /me endpoint testing"
            return self.log_result("Auth Me Endpoint", False, details, is_critical=True)
        
        try:
            me_results = []
            
            for token_name, token in tokens_to_test:
                url = f"{self.api_url}/me"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    user_data = response.json()
                    required_fields = ['id', 'email', 'username']
                    missing_fields = [field for field in required_fields if field not in user_data]
                    
                    if missing_fields:
                        me_results.append(f"{token_name}: Missing fields {missing_fields}")
                    else:
                        me_results.append(f"{token_name}: Success - {user_data.get('email', 'N/A')}")
                elif response.status_code == 401:
                    me_results.append(f"{token_name}: Unauthorized (401) - Token invalid")
                else:
                    me_results.append(f"{token_name}: Error {response.status_code}")
            
            details = "; ".join(me_results)
            
            # Check if any requests failed
            has_failures = any("error" in result.lower() or "unauthorized" in result.lower() or "missing" in result.lower() 
                             for result in me_results)
            
            return self.log_result("Auth Me Endpoint", not has_failures, details, is_critical=has_failures)
            
        except Exception as e:
            details = f"/me endpoint test failed: {str(e)}"
            return self.log_result("Auth Me Endpoint", False, details, is_critical=True)

    def test_password_comparison_logic(self):
        """Test password comparison by creating a user and immediately trying to login"""
        try:
            # Create a test user with known password
            timestamp = datetime.now().strftime('%H%M%S%f')
            test_password = "TestPassword123!"
            test_user_data = {
                "email": f"pwd_test_{timestamp}@example.com",
                "username": f"pwdtest_{timestamp}",
                "password": test_password,
                "organization": "Password Test Org"
            }
            
            # Register user
            register_url = f"{self.api_url}/register"
            headers = {'Content-Type': 'application/json'}
            
            register_response = requests.post(register_url, json=test_user_data, headers=headers, timeout=30)
            
            if register_response.status_code != 200:
                details = f"Registration failed for password test: {register_response.status_code}"
                return self.log_result("Password Comparison Logic", False, details, is_critical=True)
            
            # Immediately try to login with same credentials
            login_data = {
                "email": test_user_data["email"],
                "password": test_password
            }
            
            login_url = f"{self.api_url}/login"
            login_response = requests.post(login_url, json=login_data, headers=headers, timeout=30)
            
            if login_response.status_code == 200:
                login_data_response = login_response.json()
                if 'access_token' in login_data_response:
                    details = f"Password comparison working correctly. Register->Login cycle successful."
                    return self.log_result("Password Comparison Logic", True, details)
                else:
                    details = f"Login successful but no token returned"
                    return self.log_result("Password Comparison Logic", False, details, is_critical=True)
            elif login_response.status_code == 401:
                details = f"CRITICAL: Password comparison failing. User registered but cannot login immediately with same password."
                return self.log_result("Password Comparison Logic", False, details, is_critical=True)
            else:
                details = f"Login failed with status {login_response.status_code}: {login_response.text}"
                return self.log_result("Password Comparison Logic", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Password comparison test failed: {str(e)}"
            return self.log_result("Password Comparison Logic", False, details, is_critical=True)

    def test_backend_service_status(self):
        """Test if backend service is running and responding"""
        try:
            # Test basic connectivity
            url = f"{self.base_url}/api"
            response = requests.get(url, timeout=10)
            
            # FastAPI should return 404 for root API path, but service should be running
            if response.status_code in [404, 422]:  # 404 or 422 means service is running
                details = f"Backend service is running. Status: {response.status_code}"
                return self.log_result("Backend Service Status", True, details)
            elif response.status_code == 200:
                details = f"Backend service is running and responding. Status: {response.status_code}"
                return self.log_result("Backend Service Status", True, details)
            else:
                details = f"Backend service responding with unexpected status: {response.status_code}"
                return self.log_result("Backend Service Status", False, details, is_critical=True)
                
        except requests.exceptions.ConnectionError:
            details = f"Cannot connect to backend service at {self.base_url}"
            return self.log_result("Backend Service Status", False, details, is_critical=True)
        except Exception as e:
            details = f"Backend service test failed: {str(e)}"
            return self.log_result("Backend Service Status", False, details, is_critical=True)

    def run_comprehensive_auth_tests(self):
        """Run all authentication tests"""
        print(f"\n🚀 STARTING COMPREHENSIVE AUTHENTICATION TESTING")
        print(f"=" * 60)
        
        # Test 1: Backend Service
        self.test_backend_service_status()
        
        # Test 2: Database Connectivity
        self.test_database_connectivity()
        
        # Test 3: User Records
        self.test_user_records_in_database()
        
        # Test 4: Password Hashing
        self.test_password_hashing_verification()
        
        # Test 5: Registration
        self.test_registration_endpoint()
        
        # Test 6: Login Tests
        self.test_login_with_admin_credentials()
        self.test_login_with_test_credentials()
        self.test_login_with_new_user()
        
        # Test 7: JWT Token Validation
        self.test_jwt_token_validation()
        
        # Test 8: Auth Me Endpoint
        self.test_auth_me_endpoint()
        
        # Test 9: Password Comparison Logic
        self.test_password_comparison_logic()
        
        # Print Summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print(f"\n" + "=" * 60)
        print(f"🔍 AUTHENTICATION TESTING SUMMARY")
        print(f"=" * 60)
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            critical = " [CRITICAL]" if result["critical"] else ""
            print(f"   {status} {result['test']}{critical}")
            print(f"      {result['details']}")
        
        print(f"\n" + "=" * 60)

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_comprehensive_auth_tests()