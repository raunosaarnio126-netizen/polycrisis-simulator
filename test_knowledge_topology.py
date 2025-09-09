#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class KnowledgeTopologyTester:
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
                response = requests.get(url, headers=test_headers, timeout=120)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=120)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=120)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=120)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
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
        """Login with test credentials from review request"""
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

    def test_knowledge_topology_summary(self):
        """Test Knowledge Topology Summary endpoint"""
        success, response = self.run_test(
            "Knowledge Topology Summary",
            "GET",
            "knowledge-topology/summary",
            200
        )
        
        if success:
            print(f"   Total categories: {response.get('total_categories', 'N/A')}")
            print(f"   Total sources: {response.get('total_sources', 'N/A')}")
            print(f"   API enabled sources: {response.get('api_enabled_sources', 'N/A')}")
            print(f"   Average credibility: {response.get('average_credibility', 'N/A')}")
            print(f"   Implementation phases: {response.get('implementation_phases', 'N/A')}")
            print(f"   Access tiers: {response.get('access_tiers', [])}")
            
            # Verify expected structure
            required_fields = ['total_categories', 'total_sources', 'api_enabled_sources', 
                             'average_credibility', 'categories', 'implementation_phases', 'access_tiers']
            
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing required field: {field}")
                    return False
            
            # Verify categories structure
            categories = response.get('categories', {})
            if not categories:
                print(f"   ❌ No categories found in response")
                return False
                
            print(f"   Categories found: {len(categories)}")
            for cat_name, cat_data in categories.items():
                print(f"   - {cat_data.get('name', cat_name)}: {cat_data.get('source_count', 0)} sources")
                print(f"     Priority: {cat_data.get('priority', 'N/A')}, API sources: {cat_data.get('api_sources', 0)}")
                print(f"     Avg credibility: {cat_data.get('average_credibility', 'N/A')}")
            
            # Verify expected values based on knowledge_topology.json
            expected_categories = 8
            expected_sources = 23
            
            if response.get('total_categories') != expected_categories:
                print(f"   ⚠️ Expected {expected_categories} categories, got {response.get('total_categories')}")
            
            if response.get('total_sources') != expected_sources:
                print(f"   ⚠️ Expected {expected_sources} sources, got {response.get('total_sources')}")
                
            return True
        return False

    def test_knowledge_sources_no_filter(self):
        """Test Knowledge Sources endpoint without filters"""
        success, response = self.run_test(
            "Knowledge Sources - No Filter",
            "GET",
            "knowledge-topology/sources",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} knowledge sources")
            
            # Verify source structure
            if response:
                sample_source = response[0]
                required_fields = ['name', 'full_name', 'type', 'specialization', 'url', 
                                 'api_availability', 'content_types', 'update_frequency', 'credibility_score']
                
                for field in required_fields:
                    if field not in sample_source:
                        print(f"   ❌ Missing required field in source: {field}")
                        return False
                
                # Show sample sources
                print(f"   Sample sources (top 5):")
                for i, source in enumerate(response[:5]):
                    print(f"   {i+1}. {source.get('name')} ({source.get('type')})")
                    print(f"      Credibility: {source.get('credibility_score')}, API: {source.get('api_availability')}")
                    print(f"      Specializations: {source.get('specialization', [])}")
                
                # Verify sources are sorted by credibility (descending)
                credibility_scores = [s.get('credibility_score', 0) for s in response]
                if credibility_scores != sorted(credibility_scores, reverse=True):
                    print(f"   ⚠️ Sources may not be properly sorted by credibility score")
                else:
                    print(f"   ✅ Sources properly sorted by credibility score")
                
            return True
        return False

    def test_crisis_strategy_economic_crisis(self):
        """Test Crisis Strategy endpoint - Economic Crisis (severity 8)"""
        crisis_data = {
            "crisis_type": "economic_crisis",
            "severity_level": 8
        }
        
        success, response = self.run_test(
            "Crisis Strategy - Economic Crisis (Severity 8)",
            "POST",
            "knowledge-topology/crisis-strategy",
            200,
            data=crisis_data
        )
        
        if success:
            print(f"   Crisis type: {response.get('crisis_type', 'N/A')}")
            print(f"   Severity level: {response.get('severity_level', 'N/A')}")
            print(f"   Total recommended sources: {response.get('total_sources', 'N/A')}")
            print(f"   API sources: {response.get('api_sources', 'N/A')}")
            print(f"   Average credibility: {response.get('average_credibility', 'N/A')}")
            print(f"   Recommended access levels: {response.get('recommended_access_levels', [])}")
            
            # Verify response structure
            required_fields = ['crisis_type', 'severity_level', 'recommended_sources', 
                             'recommended_access_levels', 'total_sources', 'api_sources', 'average_credibility']
            
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing required field: {field}")
                    return False
            
            # Verify recommended sources structure
            recommended_sources = response.get('recommended_sources', [])
            if not recommended_sources:
                print(f"   ❌ No recommended sources returned")
                return False
            
            print(f"   Recommended sources:")
            for i, source in enumerate(recommended_sources[:5]):  # Show first 5
                print(f"   {i+1}. {source.get('name')} ({source.get('type')})")
                print(f"      Credibility: {source.get('credibility_score')}, API: {source.get('api_available')}")
                print(f"      Specializations: {source.get('specialization', [])}")
            
            # Verify high severity gets premium sources
            access_levels = response.get('recommended_access_levels', [])
            expected_premium_levels = ['exclusive', 'enterprise', 'premium']
            
            has_premium = any(level in access_levels for level in expected_premium_levels)
            if has_premium:
                print(f"   ✅ High severity crisis includes premium access levels")
            else:
                print(f"   ⚠️ High severity crisis missing premium access levels")
            
            return True
        return False

    def test_crisis_strategy_cyber_attack(self):
        """Test Crisis Strategy endpoint - Cyber Attack (severity 6)"""
        crisis_data = {
            "crisis_type": "cyber_attack",
            "severity_level": 6
        }
        
        success, response = self.run_test(
            "Crisis Strategy - Cyber Attack (Severity 6)",
            "POST",
            "knowledge-topology/crisis-strategy",
            200,
            data=crisis_data
        )
        
        if success:
            print(f"   Crisis type: {response.get('crisis_type', 'N/A')}")
            print(f"   Severity level: {response.get('severity_level', 'N/A')}")
            print(f"   Total recommended sources: {response.get('total_sources', 'N/A')}")
            print(f"   Average credibility: {response.get('average_credibility', 'N/A')}")
            
            # Verify cyber attack gets technology-focused sources
            recommended_sources = response.get('recommended_sources', [])
            tech_related_sources = 0
            
            for source in recommended_sources:
                specializations = [s.lower() for s in source.get('specialization', [])]
                tech_keywords = ['technology', 'digital', 'cyber', 'tech']
                if any(keyword in ' '.join(specializations) for keyword in tech_keywords):
                    tech_related_sources += 1
            
            if tech_related_sources > 0:
                print(f"   ✅ Found {tech_related_sources} technology-related sources for cyber attack")
            else:
                print(f"   ⚠️ No technology-related sources found for cyber attack")
            
            return True
        return False

    def test_crisis_strategy_pandemic(self):
        """Test Crisis Strategy endpoint - Pandemic (severity 9)"""
        crisis_data = {
            "crisis_type": "pandemic",
            "severity_level": 9
        }
        
        success, response = self.run_test(
            "Crisis Strategy - Pandemic (Severity 9)",
            "POST",
            "knowledge-topology/crisis-strategy",
            200,
            data=crisis_data
        )
        
        if success:
            print(f"   Crisis type: {response.get('crisis_type', 'N/A')}")
            print(f"   Severity level: {response.get('severity_level', 'N/A')}")
            print(f"   Total recommended sources: {response.get('total_sources', 'N/A')}")
            
            # Verify critical severity (9) gets maximum sources
            total_sources = response.get('total_sources', 0)
            if total_sources >= 8:  # Critical crises should get up to 8 sources
                print(f"   ✅ Critical pandemic crisis gets maximum sources ({total_sources})")
            else:
                print(f"   ⚠️ Critical pandemic crisis has fewer sources than expected ({total_sources})")
            
            # Verify access levels for critical crisis
            access_levels = response.get('recommended_access_levels', [])
            critical_levels = ['exclusive', 'enterprise']
            
            has_critical_access = any(level in access_levels for level in critical_levels)
            if has_critical_access:
                print(f"   ✅ Critical pandemic includes exclusive/enterprise access levels")
            else:
                print(f"   ⚠️ Critical pandemic missing exclusive/enterprise access levels")
            
            return True
        return False

def main():
    print("🧠 Testing Knowledge Topology Endpoints")
    print("=" * 50)
    
    tester = KnowledgeTopologyTester()
    
    # Login with test credentials
    print("\n🔐 Authenticating with test credentials...")
    if not tester.login_with_test_credentials():
        print("❌ Authentication failed, stopping tests")
        return 1
    
    # Run Knowledge Topology tests
    print("\n📊 Testing Knowledge Topology Summary...")
    tester.test_knowledge_topology_summary()
    
    print("\n📋 Testing Knowledge Sources...")
    tester.test_knowledge_sources_no_filter()
    
    print("\n🎯 Testing Crisis Strategy Generation...")
    tester.test_crisis_strategy_economic_crisis()
    tester.test_crisis_strategy_cyber_attack()
    tester.test_crisis_strategy_pandemic()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Knowledge Topology tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())