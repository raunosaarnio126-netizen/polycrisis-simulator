#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class CrisisFrameworkTester:
    def __init__(self, base_url="https://crisis-monitor-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
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
                response = requests.get(url, headers=test_headers, timeout=60)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=60)

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

    def login_with_test_credentials(self):
        """Login with test credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "Login with Test Credentials",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
            return True
        return False

    def test_crisis_framework_summary(self):
        """Test Crisis Framework Summary endpoint"""
        success, response = self.run_test(
            "Crisis Framework Summary",
            "GET",
            "crisis-framework/summary",
            200
        )
        
        if success:
            print(f"   Total factors: {response.get('total_factors', 'N/A')}")
            print(f"   Total monitoring tasks: {response.get('total_monitoring_tasks', 'N/A')}")
            print(f"   High priority factors: {response.get('high_priority_factors', 'N/A')}")
            print(f"   Real-time monitoring: {response.get('real_time_monitoring', 'N/A')}")
            print(f"   Categories: {response.get('categories', [])}")
            
            # Verify expected structure
            required_fields = ['total_factors', 'total_monitoring_tasks', 'high_priority_factors', 
                             'real_time_monitoring', 'categories']
            
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing required field: {field}")
                    return False
            
            return True
        return False

    def test_crisis_factors_no_filter(self):
        """Test Crisis Factors endpoint without filters"""
        success, response = self.run_test(
            "Crisis Factors - No Filter",
            "GET",
            "crisis-framework/factors",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} crisis factors")
            
            # Show sample factors
            if response:
                print(f"   Sample factors (first 2):")
                for i, factor in enumerate(response[:2]):
                    print(f"   {i+1}. {factor.get('name')} ({factor.get('category')})")
                    print(f"      Priority: {factor.get('priority')}, Impact: {factor.get('impact_scale')}")
                    
            return True
        return False

    def test_crisis_factors_category_filter(self):
        """Test Crisis Factors endpoint with category filtering"""
        success, response = self.run_test(
            "Crisis Factors - Environmental Impact Filter",
            "GET",
            "crisis-framework/factors?category=environmental_impact",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} environmental impact factors")
            
            # Verify all factors belong to environmental_impact category
            for factor in response:
                if factor.get('category_key') != 'environmental_impact':
                    print(f"   ❌ Factor from wrong category: {factor.get('category_key')}")
                    return False
                    
            return True
        return False

    def test_monitoring_tasks_no_filter(self):
        """Test Monitoring Tasks endpoint without filters"""
        success, response = self.run_test(
            "Monitoring Tasks - No Filter",
            "GET",
            "crisis-framework/monitoring-tasks",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} monitoring tasks")
            
            # Show all monitoring tasks
            if response:
                print(f"   Monitoring tasks:")
                for i, task in enumerate(response):
                    print(f"   {i+1}. {task.get('task')}")
                    print(f"      Priority: {task.get('priority')}, Frequency: {task.get('frequency')}")
                    
            return True
        return False

    def test_monitoring_tasks_priority_filter(self):
        """Test Monitoring Tasks endpoint with priority filtering"""
        success, response = self.run_test(
            "Monitoring Tasks - Critical Priority Filter",
            "GET",
            "crisis-framework/monitoring-tasks?priority=critical",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} critical priority tasks")
            
            # Verify all tasks have critical priority
            for task in response:
                if task.get('priority') != 'critical':
                    print(f"   ❌ Task with wrong priority: {task.get('priority')}")
                    return False
            
            return True
        return False

    def test_scenario_assessment(self):
        """Test Scenario Assessment with Finnish Economic Crisis scenario"""
        scenario_id = "9796a80e-976e-463d-ba00-aeb899b76a7a"
        
        success, response = self.run_test(
            "Crisis Framework Scenario Assessment",
            "POST",
            "crisis-framework/scenario-assessment",
            200,
            data={"scenario_id": scenario_id}
        )
        
        if success:
            print(f"   Scenario ID: {response.get('scenario_id')}")
            print(f"   Scenario title: {response.get('scenario_title')}")
            print(f"   Crisis type: {response.get('crisis_type')}")
            print(f"   Total relevant factors: {response.get('total_factors')}")
            print(f"   Critical monitoring tasks: {response.get('critical_monitoring_tasks')}")
            
            # Verify required fields
            required_fields = ['scenario_id', 'scenario_title', 'crisis_type', 'severity_level',
                             'relevant_factors', 'recommended_monitoring', 'assessment_timestamp',
                             'total_factors', 'critical_monitoring_tasks']
            
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing required field: {field}")
                    return False
                    
            return True
        return False

def main():
    print("🚨 Testing Crisis Management Framework Endpoints")
    print("=" * 60)
    
    tester = CrisisFrameworkTester()
    
    # Login first
    if not tester.login_with_test_credentials():
        print("❌ Failed to login, stopping tests")
        return 1
    
    # Run tests
    print("\n📊 Testing Framework Summary...")
    tester.test_crisis_framework_summary()
    
    print("\n🔍 Testing Crisis Factors...")
    tester.test_crisis_factors_no_filter()
    tester.test_crisis_factors_category_filter()
    
    print("\n📋 Testing Monitoring Tasks...")
    tester.test_monitoring_tasks_no_filter()
    tester.test_monitoring_tasks_priority_filter()
    
    print("\n🎯 Testing Scenario Assessment...")
    tester.test_scenario_assessment()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Crisis Framework tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())