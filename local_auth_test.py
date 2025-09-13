#!/usr/bin/env python3
"""
Local Authentication System Testing for Polycrisis Simulator
Testing against local backend on port 8001
"""

import requests
import sys
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

class LocalAuthTester:
    def __init__(self):
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # Local backend configuration
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        
        # Database Configuration
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        
        # Test Results
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        
        print(f"🔧 Local Authentication Tester Initialized")
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
        
        print(f"\n{status} {test_name}")
        print(f"   Details: {details}")
        
        return success

    def test_backend_connectivity(self):
        """Test local backend connectivity"""
        try:
            # Test basic connectivity to local backend
            response = requests.get(f"{self.base_url}", timeout=5)
            
            # FastAPI root should return something
            if response.status_code in [200, 404, 422]:
                details = f"Local backend is running. Status: {response.status_code}"
                return self.log_result("Local Backend Connectivity", True, details)
            else:
                details = f"Unexpected response from local backend: {response.status_code}"
                return self.log_result("Local Backend Connectivity", False, details, is_critical=True)
                
        except requests.exceptions.ConnectionError:
            details = f"Cannot connect to local backend at {self.base_url}"
            return self.log_result("Local Backend Connectivity", False, details, is_critical=True)
        except Exception as e:
            details = f"Backend connectivity test failed: {str(e)}"
            return self.log_result("Local Backend Connectivity", False, details, is_critical=True)

    def check_database_users(self):
        """Check users in database"""
        try:
            client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            db = client[self.db_name]
            users_collection = db.users
            
            # Get all users
            users = list(users_collection.find({}, {"email": 1, "password": 1}))
            
            # Check for specific users
            admin_user = users_collection.find_one({"email": "admin@test.com"})
            test_user = users_collection.find_one({"email": "test@example.com"})
            
            details = f"Total users: {len(users)}. Admin exists: {admin_user is not None}. Test user exists: {test_user is not None}"
            
            # Print some user emails for debugging
            if users:
                sample_emails = [user.get('email', 'NO_EMAIL') for user in users[:5]]
                details += f". Sample emails: {sample_emails}"
            
            return self.log_result("Database Users Check", True, details)
            
        except Exception as e:
            details = f"Database users check failed: {str(e)}"
            return self.log_result("Database Users Check", False, details, is_critical=True)

    def test_registration_endpoint(self):
        """Test user registration"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            test_user_data = {
                "email": f"local_test_{timestamp}@example.com",
                "username": f"localtest_{timestamp}",
                "password": "TestPass123!",
                "organization": "Local Test Organization"
            }
            
            url = f"{self.api_url}/register"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=test_user_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"Registration successful. Token received: {token[:50]}..."
                    self.test_user_data = test_user_data
                    self.test_token = token
                    return self.log_result("Registration Endpoint", True, details)
                else:
                    details = f"Registration response missing token: {response_data}"
                    return self.log_result("Registration Endpoint", False, details, is_critical=True)
            else:
                details = f"Registration failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Registration Endpoint", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Registration test failed: {str(e)}"
            return self.log_result("Registration Endpoint", False, details, is_critical=True)

    def test_login_with_known_user(self):
        """Test login with a known user from database"""
        try:
            # First, let's get a user from the database
            client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            db = client[self.db_name]
            users_collection = db.users
            
            # Get the test user
            test_user = users_collection.find_one({"email": "test@example.com"})
            
            if not test_user:
                details = "test@example.com user not found in database"
                return self.log_result("Login with Known User", False, details, is_critical=True)
            
            # Try to login with the known password
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            url = f"{self.api_url}/login"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=login_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"Login successful with test@example.com. Token: {token[:50]}..."
                    self.known_user_token = token
                    return self.log_result("Login with Known User", True, details)
                else:
                    details = f"Login response missing token: {response_data}"
                    return self.log_result("Login with Known User", False, details, is_critical=True)
            elif response.status_code == 401:
                details = f"Login failed - Invalid credentials (401). CRITICAL: Password verification failing"
                return self.log_result("Login with Known User", False, details, is_critical=True)
            else:
                details = f"Login failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Login with Known User", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Known user login test failed: {str(e)}"
            return self.log_result("Login with Known User", False, details, is_critical=True)

    def test_login_with_new_user(self):
        """Test login with newly registered user"""
        if not hasattr(self, 'test_user_data'):
            details = "No test user data available from registration"
            return self.log_result("Login with New User", False, details, is_critical=True)
        
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            url = f"{self.api_url}/login"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=login_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"New user login successful. Token: {token[:50]}..."
                    return self.log_result("Login with New User", True, details)
                else:
                    details = f"New user login response missing token: {response_data}"
                    return self.log_result("Login with New User", False, details, is_critical=True)
            elif response.status_code == 401:
                details = f"New user login failed - Invalid credentials (401). CRITICAL: Registration->Login cycle broken"
                return self.log_result("Login with New User", False, details, is_critical=True)
            else:
                details = f"New user login failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Login with New User", False, details, is_critical=True)
                
        except Exception as e:
            details = f"New user login test failed: {str(e)}"
            return self.log_result("Login with New User", False, details, is_critical=True)

    def test_me_endpoint(self):
        """Test /api/me endpoint"""
        tokens_to_test = []
        
        if hasattr(self, 'known_user_token'):
            tokens_to_test.append(("Known User", self.known_user_token))
        if hasattr(self, 'test_token'):
            tokens_to_test.append(("New User", self.test_token))
        
        if not tokens_to_test:
            details = "No tokens available for /me endpoint testing"
            return self.log_result("Me Endpoint", False, details, is_critical=True)
        
        try:
            results = []
            
            for token_name, token in tokens_to_test:
                url = f"{self.api_url}/me"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    results.append(f"{token_name}: Success - {user_data.get('email', 'N/A')}")
                elif response.status_code == 401:
                    results.append(f"{token_name}: Unauthorized (401)")
                else:
                    results.append(f"{token_name}: Error {response.status_code}")
            
            details = "; ".join(results)
            has_failures = any("error" in result.lower() or "unauthorized" in result.lower() for result in results)
            
            return self.log_result("Me Endpoint", not has_failures, details, is_critical=has_failures)
            
        except Exception as e:
            details = f"/me endpoint test failed: {str(e)}"
            return self.log_result("Me Endpoint", False, details, is_critical=True)

    def test_admin_user_creation(self):
        """Create admin user for testing"""
        try:
            admin_user_data = {
                "email": "admin@test.com",
                "username": "admin",
                "password": "admin123",
                "organization": "Admin Organization"
            }
            
            url = f"{self.api_url}/register"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=admin_user_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    details = f"Admin user created successfully. Token: {token[:50]}..."
                    self.admin_token = token
                    return self.log_result("Admin User Creation", True, details)
                else:
                    details = f"Admin creation response missing token: {response_data}"
                    return self.log_result("Admin User Creation", False, details)
            elif response.status_code == 400:
                # User might already exist
                details = f"Admin user might already exist (400). Trying login instead."
                
                # Try to login with admin credentials
                login_data = {
                    "email": "admin@test.com",
                    "password": "admin123"
                }
                
                login_response = requests.post(f"{self.api_url}/login", json=login_data, headers=headers, timeout=10)
                
                if login_response.status_code == 200:
                    login_data_response = login_response.json()
                    if 'access_token' in login_data_response:
                        token = login_data_response['access_token']
                        details += f" Login successful. Token: {token[:50]}..."
                        self.admin_token = token
                        return self.log_result("Admin User Creation", True, details)
                
                details += f" Login also failed: {login_response.status_code}"
                return self.log_result("Admin User Creation", False, details, is_critical=True)
            else:
                details = f"Admin creation failed. Status: {response.status_code}, Response: {response.text}"
                return self.log_result("Admin User Creation", False, details, is_critical=True)
                
        except Exception as e:
            details = f"Admin user creation test failed: {str(e)}"
            return self.log_result("Admin User Creation", False, details, is_critical=True)

    def run_all_tests(self):
        """Run all authentication tests"""
        print(f"\n🚀 STARTING LOCAL AUTHENTICATION TESTING")
        print(f"=" * 60)
        
        # Test 1: Backend Connectivity
        self.test_backend_connectivity()
        
        # Test 2: Database Users
        self.check_database_users()
        
        # Test 3: Registration
        self.test_registration_endpoint()
        
        # Test 4: Login with known user
        self.test_login_with_known_user()
        
        # Test 5: Login with new user
        self.test_login_with_new_user()
        
        # Test 6: Me endpoint
        self.test_me_endpoint()
        
        # Test 7: Admin user creation/login
        self.test_admin_user_creation()
        
        # Print Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "=" * 60)
        print(f"🔍 LOCAL AUTHENTICATION TESTING SUMMARY")
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
        
        print(f"\n" + "=" * 60)

if __name__ == "__main__":
    tester = LocalAuthTester()
    tester.run_all_tests()