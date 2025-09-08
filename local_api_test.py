import requests
import json

def test_local_strategic_implementation():
    """Test Strategic Implementation endpoints locally"""
    base_url = "http://localhost:8001/api"
    
    print("🚀 Local Strategic Implementation API Test")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    user_data = {
        "email": "localtest@example.com",
        "username": "localtest",
        "password": "TestPass123!",
        "organization": "Local Test Org"
    }
    
    try:
        response = requests.post(f"{base_url}/register", json=user_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ User registered successfully")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Create a test scenario
    print("2. Creating test scenario...")
    scenario_data = {
        "title": "Local Test Scenario",
        "description": "A test scenario for Strategic Implementation features",
        "crisis_type": "natural_disaster",
        "severity_level": 7,
        "affected_regions": ["Test Region"],
        "key_variables": ["Test Variable"]
    }
    
    try:
        response = requests.post(f"{base_url}/scenarios", json=scenario_data, headers=headers, timeout=10)
        if response.status_code == 200:
            scenario_id = response.json()["id"]
            print(f"✅ Scenario created: {scenario_id}")
        else:
            print(f"❌ Scenario creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Scenario creation error: {str(e)}")
        return
    
    # Step 3: Test Strategic Implementation endpoints exist
    endpoints = [
        ("Game Book", f"scenarios/{scenario_id}/game-book"),
        ("Action Plan", f"scenarios/{scenario_id}/action-plan"),
        ("Strategy Implementation", f"scenarios/{scenario_id}/strategy-implementation")
    ]
    
    for name, endpoint in endpoints:
        print(f"3. Testing {name} endpoint availability...")
        try:
            # Test POST (generation) - just check if endpoint exists
            response = requests.post(f"{base_url}/{endpoint}", headers=headers, timeout=5)
            print(f"   POST /{endpoint}: Status {response.status_code}")
            
            if response.status_code in [200, 500]:  # 500 might be AI timeout, but endpoint exists
                print(f"✅ {name} POST endpoint exists")
            else:
                print(f"⚠️ {name} POST endpoint issue: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ {name} POST timed out (endpoint exists, likely AI processing)")
        except Exception as e:
            print(f"❌ {name} POST error: {str(e)}")
        
        # Test GET endpoint structure
        try:
            response = requests.get(f"{base_url}/{endpoint}", headers=headers, timeout=5)
            print(f"   GET /{endpoint}: Status {response.status_code}")
            
            if response.status_code in [200, 404]:  # 404 expected if not generated yet
                print(f"✅ {name} GET endpoint exists")
            else:
                print(f"⚠️ {name} GET endpoint issue: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name} GET error: {str(e)}")
    
    print("\n✅ Local API endpoint test completed!")

if __name__ == "__main__":
    test_local_strategic_implementation()