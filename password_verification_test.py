#!/usr/bin/env python3
"""
Password Verification Test - Direct Testing of Password Logic
"""

import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import bcrypt

def test_password_verification():
    # Load environment variables
    load_dotenv('/app/backend/.env')
    
    # Configuration
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    print("🔐 PASSWORD VERIFICATION DIAGNOSIS")
    print("=" * 50)
    
    # Initialize password context (same as in server.py)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # 1. Check Database Users and their password hashes
    print("\n1. DATABASE PASSWORD ANALYSIS:")
    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        users_collection = db.users
        
        # Get test user
        test_user = users_collection.find_one({"email": "test@example.com"})
        
        if not test_user:
            print("   ❌ test@example.com user not found")
            return
        
        stored_hash = test_user.get('password', '')
        print(f"   ✅ Found test@example.com user")
        print(f"   🔑 Stored password hash: {stored_hash}")
        print(f"   📏 Hash length: {len(stored_hash)}")
        print(f"   🏷️  Hash format: {'bcrypt' if stored_hash.startswith('$2b$') else 'unknown'}")
        
        # 2. Test password verification with known password
        print("\n2. PASSWORD VERIFICATION TEST:")
        test_password = "password123"
        
        print(f"   🧪 Testing password: '{test_password}'")
        print(f"   🔍 Against stored hash: {stored_hash[:50]}...")
        
        # Test with passlib (same as server.py)
        try:
            is_valid_passlib = pwd_context.verify(test_password, stored_hash)
            print(f"   📊 Passlib verification result: {is_valid_passlib}")
        except Exception as e:
            print(f"   ❌ Passlib verification error: {str(e)}")
            is_valid_passlib = False
        
        # Test with direct bcrypt
        try:
            is_valid_bcrypt = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"   📊 Direct bcrypt verification result: {is_valid_bcrypt}")
        except Exception as e:
            print(f"   ❌ Direct bcrypt verification error: {str(e)}")
            is_valid_bcrypt = False
        
        # 3. Test hash generation
        print("\n3. HASH GENERATION TEST:")
        
        # Generate new hash for the same password
        new_hash_passlib = pwd_context.hash(test_password)
        new_hash_bcrypt = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        print(f"   🔨 New passlib hash: {new_hash_passlib}")
        print(f"   🔨 New bcrypt hash: {new_hash_bcrypt}")
        
        # Verify new hashes work
        verify_new_passlib = pwd_context.verify(test_password, new_hash_passlib)
        verify_new_bcrypt = bcrypt.checkpw(test_password.encode('utf-8'), new_hash_bcrypt.encode('utf-8'))
        
        print(f"   ✅ New passlib hash verifies: {verify_new_passlib}")
        print(f"   ✅ New bcrypt hash verifies: {verify_new_bcrypt}")
        
        # 4. Test with different passwords
        print("\n4. WRONG PASSWORD TEST:")
        wrong_passwords = ["password124", "Password123", "password", "admin123"]
        
        for wrong_pwd in wrong_passwords:
            try:
                result = pwd_context.verify(wrong_pwd, stored_hash)
                print(f"   🚫 '{wrong_pwd}' -> {result} (should be False)")
            except Exception as e:
                print(f"   ❌ Error testing '{wrong_pwd}': {str(e)}")
        
        # 5. Check if there are other users with different password patterns
        print("\n5. OTHER USERS ANALYSIS:")
        other_users = list(users_collection.find({}, {"email": 1, "password": 1}).limit(5))
        
        for user in other_users:
            email = user.get('email', 'NO_EMAIL')
            password_hash = user.get('password', 'NO_PASSWORD')
            hash_format = 'bcrypt' if password_hash.startswith('$2b$') else 'unknown'
            print(f"   👤 {email}: {hash_format} ({len(password_hash)} chars)")
        
        # 6. DIAGNOSIS SUMMARY
        print("\n6. DIAGNOSIS SUMMARY:")
        if is_valid_passlib and is_valid_bcrypt:
            print("   ✅ Password verification is working correctly")
            print("   🔍 The issue might be elsewhere (API routing, request handling, etc.)")
        elif not is_valid_passlib and not is_valid_bcrypt:
            print("   ❌ CRITICAL: Password verification is completely broken")
            print("   🔍 The stored hash does not match the expected password")
            print("   💡 Possible causes:")
            print("      - Wrong password being tested")
            print("      - Hash was generated with different algorithm/settings")
            print("      - Database corruption")
        else:
            print("   ⚠️  Mixed results - one method works, other doesn't")
            print("   🔍 This suggests a library compatibility issue")
        
        # 7. Test creating admin user hash
        print("\n7. ADMIN USER HASH GENERATION:")
        admin_password = "admin123"
        admin_hash = pwd_context.hash(admin_password)
        admin_verify = pwd_context.verify(admin_password, admin_hash)
        
        print(f"   🔨 Generated hash for 'admin123': {admin_hash}")
        print(f"   ✅ Verification test: {admin_verify}")
        
        # Insert admin user if it doesn't exist
        admin_exists = users_collection.find_one({"email": "admin@test.com"})
        if not admin_exists:
            print("   📝 Creating admin@test.com user...")
            admin_user_doc = {
                "id": "admin-user-id-12345",
                "email": "admin@test.com",
                "username": "admin",
                "organization": "Admin Organization",
                "password": admin_hash,
                "created_at": "2025-01-01T00:00:00Z"
            }
            
            try:
                users_collection.insert_one(admin_user_doc)
                print("   ✅ Admin user created successfully")
            except Exception as e:
                print(f"   ❌ Failed to create admin user: {str(e)}")
        else:
            print("   ℹ️  Admin user already exists")
        
    except Exception as e:
        print(f"   ❌ Database analysis failed: {str(e)}")
        return
    
    print("\n" + "=" * 50)
    print("🏁 PASSWORD VERIFICATION DIAGNOSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_password_verification()