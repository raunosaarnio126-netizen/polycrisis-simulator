#!/usr/bin/env python3
"""
Quick test to verify monitoring endpoints exist
"""
import requests
import json

def test_endpoint_exists(url, method="GET"):
    """Test if an endpoint exists (returns 401/405 instead of 404)"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        
        # 404 means endpoint doesn't exist
        # 401/405/422 means endpoint exists but needs auth/wrong method/bad data
        if response.status_code == 404:
            return False, f"404 Not Found"
        else:
            return True, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    base_url = "https://crisis-adapt.preview.emergentagent.com/api"
    test_scenario_id = "test-scenario-id"
    
    print("🔍 Testing Intelligent Monitoring Network Endpoints")
    print("=" * 60)
    
    # Test monitoring endpoints
    endpoints_to_test = [
        ("Smart Monitoring Suggestions", f"{base_url}/scenarios/{test_scenario_id}/suggest-monitoring-sources", "POST"),
        ("Add Monitoring Source", f"{base_url}/scenarios/{test_scenario_id}/add-monitoring-source", "POST"),
        ("Get Monitoring Sources", f"{base_url}/scenarios/{test_scenario_id}/monitoring-sources", "GET"),
        ("Collect Data", f"{base_url}/scenarios/{test_scenario_id}/collect-data", "POST"),
        ("Monitoring Dashboard", f"{base_url}/scenarios/{test_scenario_id}/monitoring-dashboard", "GET"),
    ]
    
    # Test existing endpoints for comparison
    existing_endpoints = [
        ("Get Scenarios", f"{base_url}/scenarios", "GET"),
        ("AI Genie", f"{base_url}/ai-genie", "POST"),
        ("Dashboard Stats", f"{base_url}/dashboard/stats", "GET"),
        ("Advanced Analytics", f"{base_url}/dashboard/advanced-analytics", "GET"),
    ]
    
    print("\n📊 Testing New Monitoring Endpoints:")
    monitoring_results = []
    for name, url, method in endpoints_to_test:
        exists, status = test_endpoint_exists(url, method)
        status_icon = "✅" if exists else "❌"
        print(f"{status_icon} {name}: {status}")
        monitoring_results.append((name, exists))
    
    print("\n📋 Testing Existing Endpoints (for comparison):")
    existing_results = []
    for name, url, method in existing_endpoints:
        exists, status = test_endpoint_exists(url, method)
        status_icon = "✅" if exists else "❌"
        print(f"{status_icon} {name}: {status}")
        existing_results.append((name, exists))
    
    # Summary
    monitoring_working = sum(1 for _, exists in monitoring_results if exists)
    existing_working = sum(1 for _, exists in existing_results if exists)
    
    print("\n" + "=" * 60)
    print("📈 ENDPOINT AVAILABILITY SUMMARY")
    print("=" * 60)
    print(f"🌐 New Monitoring Endpoints: {monitoring_working}/{len(monitoring_results)} available")
    print(f"📋 Existing Endpoints: {existing_working}/{len(existing_results)} available")
    
    if monitoring_working == len(monitoring_results):
        print("🎉 ALL MONITORING ENDPOINTS ARE IMPLEMENTED!")
    elif monitoring_working > 0:
        print(f"⚠️  {len(monitoring_results) - monitoring_working} monitoring endpoints missing")
    else:
        print("❌ NO MONITORING ENDPOINTS FOUND")
    
    return monitoring_working == len(monitoring_results)

if __name__ == "__main__":
    main()