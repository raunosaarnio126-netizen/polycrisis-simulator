#!/usr/bin/env python3
"""
Simple Authentication Test - Direct API Testing
"""

import requests
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

def test_auth_system():
    # Load environment variables
    load_dotenv('/app/backend/.env')
    
    # Configuration
    external_url = "https://adapt-crisis-sim.preview.emergentagent.com/api"
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    print("🔍 AUTHENTICATION SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    # 1. Check Database Users
    print("\n1. DATABASE USERS CHECK:")
    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        users_collection = db.users
        
        total_users = users_collection.count_documents({})
        test_user = users_collection.find_one({"email": "test@example.com"})
        admin_user = users_collection.find_one({"email": "admin@test.com"})
        
        print(f"   ✅ Database connected successfully")
        print(f"   📊 Total users in database: {total_users}")
        print(f"   👤 test@example.com exists: {test_user is not None}")
        print(f"   👤 admin@test.com exists: {admin_user is not None}")
        
        if test_user:
            print(f"   🔑 test@example.com password hash: {test_user.get('password', 'NO_PASSWORD')[:50]}...")
        
        # Show some sample users
        sample_users = list(users_collection.find({}, {"email": 1}).limit(5))
        sample_emails = [user.get('email') for user in sample_users]
        print(f"   📝 Sample user emails: {sample_emails}")
        
    except Exception as e:
        print(f"   ❌ Database check failed: {str(e)}")
        return
    
    # 2. Test Registration
    print("\n2. REGISTRATION TEST:")
    try:
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "email": f"auth_diagnosis_{timestamp}@example.com",
            "username": f"authdiag_{timestamp}",
            "password": "TestPass123!",
            "organization": "Auth Diagnosis Org"
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{external_url}/register", json=test_user_data, headers=headers, timeout=60)
        
        print(f"   📡 Registration request sent to: {external_url}/register")
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if 'access_token' in response_data:
                token = response_data['access_token']
                print(f"   ✅ Registration successful!")
                print(f"   🎫 Token received: {token[:50]}...")
                
                # Store for login test
                registration_token = token
                registration_user = test_user_data
            else:
                print(f"   ❌ Registration response missing token: {response_data}")
                return
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Registration test failed: {str(e)}")
        return
    
    # 3. Test Login with newly registered user
    print("\n3. LOGIN TEST (New User):")
    try:
        login_data = {
            "email": registration_user["email"],
            "password": registration_user["password"]
        }
        
        response = requests.post(f"{external_url}/login", json=login_data, headers=headers, timeout=60)
        
        print(f"   📡 Login request sent to: {external_url}/login")
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if 'access_token' in response_data:
                token = response_data['access_token']
                print(f"   ✅ Login successful!")
                print(f"   🎫 Token received: {token[:50]}...")
                login_token = token
            else:
                print(f"   ❌ Login response missing token: {response_data}")
                return
        elif response.status_code == 401:
            print(f"   ❌ CRITICAL: Login failed with 401 - Invalid credentials")
            print(f"   🔍 This indicates password verification is failing")
            print(f"   📝 Response: {response.text}")
            return
        else:
            print(f"   ❌ Login failed with status {response.status_code}: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Login test failed: {str(e)}")
        return
    
    # 4. Test Login with existing user
    print("\n4. LOGIN TEST (Existing User):")
    try:
        existing_login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{external_url}/login", json=existing_login_data, headers=headers, timeout=60)
        
        print(f"   📡 Login request sent for test@example.com")
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if 'access_token' in response_data:
                token = response_data['access_token']
                print(f"   ✅ Existing user login successful!")
                print(f"   🎫 Token received: {token[:50]}...")
            else:
                print(f"   ❌ Login response missing token: {response_data}")
        elif response.status_code == 401:
            print(f"   ❌ CRITICAL: Existing user login failed with 401")
            print(f"   🔍 This confirms password verification is broken")
            print(f"   📝 Response: {response.text}")
        else:
            print(f"   ❌ Existing user login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Existing user login test failed: {str(e)}")
    
    # 5. Test /me endpoint
    print("\n5. AUTH VERIFICATION TEST:")
    try:
        auth_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {login_token}'
        }
        
        response = requests.get(f"{external_url}/me", headers=auth_headers, timeout=30)
        
        print(f"   📡 /me request sent")
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Auth verification successful!")
            print(f"   👤 User: {user_data.get('email', 'N/A')}")
            print(f"   🆔 User ID: {user_data.get('id', 'N/A')}")
        elif response.status_code == 401:
            print(f"   ❌ Auth verification failed - Token invalid")
        else:
            print(f"   ❌ Auth verification failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Auth verification test failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 AUTHENTICATION DIAGNOSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_system()