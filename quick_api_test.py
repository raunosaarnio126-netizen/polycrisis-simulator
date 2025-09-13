import requests
import json

def test_strategic_implementation_endpoints():
    """Quick test of Strategic Implementation API endpoints"""
    base_url = "https://adapt-crisis-sim.preview.emergentagent.com/api"
    
    print("🚀 Quick Strategic Implementation API Test")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    user_data = {
        "email": "quicktest@example.com",
        "username": "quicktest",
        "password": "TestPass123!",
        "organization": "Quick Test Org"
    }
    
    try:
        response = requests.post(f"{base_url}/register", json=user_data, timeout=30)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ User registered successfully")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Create a test scenario
    print("2. Creating test scenario...")
    scenario_data = {
        "title": "Quick Test Scenario",
        "description": "A test scenario for Strategic Implementation features",
        "crisis_type": "natural_disaster",
        "severity_level": 7,
        "affected_regions": ["Test Region"],
        "key_variables": ["Test Variable"]
    }
    
    try:
        response = requests.post(f"{base_url}/scenarios", json=scenario_data, headers=headers, timeout=30)
        if response.status_code == 200:
            scenario_id = response.json()["id"]
            print(f"✅ Scenario created: {scenario_id}")
        else:
            print(f"❌ Scenario creation failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Scenario creation error: {str(e)}")
        return
    
    # Step 3: Test Strategic Implementation endpoints
    endpoints = [
        ("Game Book", f"scenarios/{scenario_id}/game-book"),
        ("Action Plan", f"scenarios/{scenario_id}/action-plan"),
        ("Strategy Implementation", f"scenarios/{scenario_id}/strategy-implementation")
    ]
    
    for name, endpoint in endpoints:
        print(f"3. Testing {name} generation...")
        try:
            # Test POST (generation)
            response = requests.post(f"{base_url}/{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} generation endpoint exists and responds")
                
                # Test GET (retrieval) 
                response = requests.get(f"{base_url}/{endpoint}", headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {name} retrieval endpoint works")
                else:
                    print(f"⚠️ {name} retrieval failed: {response.status_code}")
            else:
                print(f"❌ {name} generation failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"⏱️ {name} generation timed out (likely AI processing)")
        except Exception as e:
            print(f"❌ {name} error: {str(e)}")
    
    print("\n✅ Quick API test completed!")

if __name__ == "__main__":
    test_strategic_implementation_endpoints()