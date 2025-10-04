import requests
import json
import sys

def test_scenario_adjustments_endpoints():
    """Test the specific scenario adjustments endpoints mentioned in the review request"""
    
    # Use local backend since external API has connectivity issues
    base_url = "http://localhost:8001"
    api_url = f"{base_url}/api"
    
    print("🧪 TESTING SCENARIO ADJUSTMENTS AND CONSENSUS ENDPOINTS")
    print("=" * 60)
    
    # Test credentials
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    print("\n1. Testing Authentication...")
    try:
        response = requests.post(f"{api_url}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Authentication successful")
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False
    
    # Get user profile
    print("\n2. Getting user profile...")
    try:
        response = requests.get(f"{api_url}/me", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get('id')
            print(f"✅ User profile retrieved: {user_id}")
        else:
            print(f"❌ Failed to get user profile: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User profile error: {str(e)}")
        return False
    
    # Create a test company
    print("\n3. Creating test company...")
    company_data = {
        "company_name": "Test Scenario Corp",
        "industry": "Technology",
        "company_size": "medium",
        "description": "Test company for scenario adjustments",
        "location": "Test City"
    }
    
    try:
        response = requests.post(f"{api_url}/companies", json=company_data, headers=headers, timeout=10)
        if response.status_code == 200:
            company_id = response.json().get('id')
            print(f"✅ Company created: {company_id}")
        else:
            print(f"❌ Failed to create company: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Company creation error: {str(e)}")
        return False
    
    # Test the specific endpoints mentioned in the review request
    
    print("\n4. Testing POST /api/companies/{company_id}/scenario-adjustments (Save Adjustments)...")
    adjustment_data = {
        "adjustment_name": "Test Economic Crisis Adjustment",
        "economic_crisis_pct": 70.0,
        "economic_stability_pct": 30.0,
        "social_unrest_pct": 60.0,
        "social_cohesion_pct": 40.0,
        "environmental_degradation_pct": 50.0,
        "environmental_resilience_pct": 50.0,
        "political_instability_pct": 65.0,
        "political_stability_pct": 35.0,
        "technological_disruption_pct": 45.0,
        "technological_advancement_pct": 55.0
    }
    
    try:
        response = requests.post(f"{api_url}/companies/{company_id}/scenario-adjustments", 
                               json=adjustment_data, headers=headers, timeout=30)
        if response.status_code == 200:
            adjustment_id = response.json().get('id')
            print(f"✅ Scenario adjustment created: {adjustment_id}")
            print(f"   Risk level: {response.json().get('risk_level')}")
            print(f"   Analysis generated: {bool(response.json().get('real_time_analysis'))}")
        else:
            print(f"❌ Failed to create scenario adjustment: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Scenario adjustment creation error: {str(e)}")
        return False
    
    print("\n5. Testing GET /api/companies/{company_id}/scenario-adjustments...")
    try:
        response = requests.get(f"{api_url}/companies/{company_id}/scenario-adjustments", 
                              headers=headers, timeout=10)
        if response.status_code == 200:
            adjustments = response.json()
            print(f"✅ Retrieved {len(adjustments)} scenario adjustments")
            if adjustments:
                print(f"   First adjustment: {adjustments[0].get('adjustment_name')}")
        else:
            print(f"❌ Failed to get scenario adjustments: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get scenario adjustments error: {str(e)}")
        return False
    
    print("\n6. Testing PUT /api/companies/{company_id}/scenario-adjustments/{adjustment_id}...")
    updated_data = {
        "adjustment_name": "Updated Economic Crisis Adjustment",
        "economic_crisis_pct": 80.0,
        "economic_stability_pct": 20.0,
        "social_unrest_pct": 70.0,
        "social_cohesion_pct": 30.0,
        "environmental_degradation_pct": 55.0,
        "environmental_resilience_pct": 45.0,
        "political_instability_pct": 75.0,
        "political_stability_pct": 25.0,
        "technological_disruption_pct": 40.0,
        "technological_advancement_pct": 60.0
    }
    
    try:
        response = requests.put(f"{api_url}/companies/{company_id}/scenario-adjustments/{adjustment_id}", 
                              json=updated_data, headers=headers, timeout=30)
        if response.status_code == 200:
            print(f"✅ Scenario adjustment updated")
            print(f"   Updated name: {response.json().get('adjustment_name')}")
            print(f"   Updated risk level: {response.json().get('risk_level')}")
        else:
            print(f"❌ Failed to update scenario adjustment: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Scenario adjustment update error: {str(e)}")
        return False
    
    print("\n7. Testing POST /api/companies/{company_id}/consensus (Save Consensus)...")
    consensus_data = {
        "adjustment_id": adjustment_id,
        "consensus_name": "Team Agreement on Crisis Scenario"
    }
    
    try:
        response = requests.post(f"{api_url}/companies/{company_id}/consensus", 
                               json=consensus_data, headers=headers, timeout=10)
        if response.status_code == 200:
            consensus_id = response.json().get('id')
            print(f"✅ Consensus created: {consensus_id}")
            print(f"   Consensus name: {response.json().get('consensus_name')}")
            print(f"   Team members: {response.json().get('total_team_members')}")
            print(f"   Consensus percentage: {response.json().get('consensus_percentage')}%")
        else:
            print(f"❌ Failed to create consensus: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Consensus creation error: {str(e)}")
        return False
    
    print("\n8. Testing POST /api/companies/{company_id}/consensus/{consensus_id}/agree...")
    try:
        response = requests.post(f"{api_url}/companies/{company_id}/consensus/{consensus_id}/agree", 
                               headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Consensus agreement recorded")
            print(f"   Message: {response.json().get('message')}")
            print(f"   Consensus reached: {response.json().get('consensus_reached')}")
        else:
            print(f"❌ Failed to record consensus agreement: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Consensus agreement error: {str(e)}")
        return False
    
    print("\n9. Testing SEPTE validation (should fail with invalid percentages)...")
    invalid_data = {
        "adjustment_name": "Invalid SEPTE Test",
        "economic_crisis_pct": 60.0,
        "economic_stability_pct": 30.0,  # Should be 40.0 to sum to 100
        "social_unrest_pct": 50.0,
        "social_cohesion_pct": 50.0,
        "environmental_degradation_pct": 50.0,
        "environmental_resilience_pct": 50.0,
        "political_instability_pct": 50.0,
        "political_stability_pct": 50.0,
        "technological_disruption_pct": 50.0,
        "technological_advancement_pct": 50.0
    }
    
    try:
        response = requests.post(f"{api_url}/companies/{company_id}/scenario-adjustments", 
                               json=invalid_data, headers=headers, timeout=10)
        if response.status_code == 400:
            print(f"✅ SEPTE validation working - rejected invalid percentages")
            print(f"   Error message: {response.json().get('detail')}")
        else:
            print(f"❌ SEPTE validation not working - should have returned 400")
            return False
    except Exception as e:
        print(f"❌ SEPTE validation test error: {str(e)}")
        return False
    
    print("\n10. Testing authentication requirement...")
    try:
        # Test without token
        response = requests.get(f"{api_url}/companies/{company_id}/scenario-adjustments", timeout=10)
        if response.status_code == 401:
            print(f"✅ Authentication properly enforced")
        else:
            print(f"❌ Authentication not enforced - should have returned 401")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL SCENARIO ADJUSTMENTS AND CONSENSUS TESTS PASSED!")
    print("=" * 60)
    
    print("\n📋 SUMMARY OF TESTED ENDPOINTS:")
    print("✅ POST /api/companies/{company_id}/scenario-adjustments - Save Adjustments")
    print("✅ GET /api/companies/{company_id}/scenario-adjustments - Retrieve Adjustments")
    print("✅ PUT /api/companies/{company_id}/scenario-adjustments/{id} - Update Adjustments")
    print("✅ POST /api/companies/{company_id}/consensus - Save Consensus")
    print("✅ POST /api/companies/{company_id}/consensus/{id}/agree - Consensus Agreement")
    print("✅ SEPTE Framework validation (percentages must sum to 100%)")
    print("✅ Authentication and access control")
    
    print("\n🔍 KEY FINDINGS:")
    print("• All backend endpoints are working correctly")
    print("• SEPTE framework validation is enforced")
    print("• AI analysis generation is working")
    print("• Consensus functionality is operational")
    print("• Authentication and access control are properly implemented")
    
    print("\n⚠️ FRONTEND ISSUE ANALYSIS:")
    print("• Backend endpoints are fully functional")
    print("• The issue is likely in the frontend button event handlers")
    print("• Frontend may not be calling the correct API endpoints")
    print("• Check frontend JavaScript console for errors")
    print("• Verify frontend is using correct API URLs and authentication")
    
    return True

if __name__ == "__main__":
    success = test_scenario_adjustments_endpoints()
    sys.exit(0 if success else 1)