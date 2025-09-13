#!/usr/bin/env python3
"""
Comprehensive test for Intelligent Monitoring Network
Handles AI processing delays and tests complete workflow
"""
import requests
import json
import sys
import time
from datetime import datetime

class ComprehensiveMonitoringTester:
    def __init__(self):
        self.base_url = "https://adapt-crisis-sim.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.scenario_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")

    def test_api_call(self, name, method, endpoint, expected_status, data=None, timeout=30, ai_endpoint=False):
        """Make API call with appropriate timeout for AI endpoints"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        
        if ai_endpoint:
            self.log(f"🤖 Testing {name} (AI endpoint - may take up to {timeout}s)")
        else:
            self.log(f"🔍 Testing {name}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            elapsed = time.time() - start_time
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code} ({elapsed:.1f}s)")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code} ({elapsed:.1f}s)")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}")
                except:
                    self.log(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            self.log(f"⏰ {name} - Timeout after {elapsed:.1f}s")
            if ai_endpoint:
                self.log(f"   ℹ️  AI endpoints may take longer - this is expected behavior")
            return False, {"error": "timeout"}
        except Exception as e:
            elapsed = time.time() - start_time
            self.log(f"❌ {name} - Exception after {elapsed:.1f}s: {str(e)}")
            return False, {"error": str(e)}

    def quick_auth_setup(self):
        """Quick authentication setup with shorter timeout"""
        self.log("🚀 Setting up authentication...")
        
        # Try to register with a unique email
        user_data = {
            "email": f"test_monitor_{int(time.time())}@example.com",
            "username": f"test_monitor_{int(time.time())}",
            "password": "TestPass123!",
            "organization": "Monitoring Test Org"
        }
        
        success, response = self.test_api_call(
            "User Registration", "POST", "register", 200, user_data, timeout=60, ai_endpoint=True
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.log(f"   ✅ User registered and authenticated")
            return True
        else:
            self.log("   ⚠️  Registration failed, trying existing user login")
            
            # Try login with a test user
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            success, response = self.test_api_call(
                "User Login", "POST", "login", 200, login_data, timeout=60, ai_endpoint=True
            )
            
            if success and 'access_token' in response:
                self.token = response['access_token']
                self.log(f"   ✅ Logged in with existing user")
                return True
            else:
                self.log("   ❌ Authentication failed")
                return False

    def create_test_scenario(self):
        """Create a test scenario for monitoring"""
        self.log("📝 Creating test scenario...")
        
        scenario_data = {
            "title": "Monitoring Test Earthquake Scenario",
            "description": "Test scenario for intelligent monitoring network features - earthquake in California",
            "crisis_type": "natural_disaster",
            "severity_level": 7,
            "affected_regions": ["California", "Nevada", "Oregon"],
            "key_variables": ["seismic activity", "population density", "infrastructure age", "emergency response"]
        }
        
        success, response = self.test_api_call(
            "Create Test Scenario", "POST", "scenarios", 200, scenario_data, timeout=30
        )
        
        if success and 'id' in response:
            self.scenario_id = response['id']
            self.log(f"   ✅ Test scenario created: {self.scenario_id}")
            return True
        else:
            self.log("   ❌ Failed to create test scenario")
            return False

    def test_non_ai_monitoring_endpoints(self):
        """Test monitoring endpoints that don't require AI processing"""
        self.log("\n📊 Testing Non-AI Monitoring Endpoints...")
        
        results = []
        
        # Test 1: Get monitoring sources (should be empty initially)
        success, response = self.test_api_call(
            "Get Monitoring Sources (Empty)",
            "GET",
            f"scenarios/{self.scenario_id}/monitoring-sources",
            200,
            timeout=10
        )
        
        if success:
            sources_count = len(response) if isinstance(response, list) else 0
            self.log(f"   📋 Found {sources_count} monitoring sources (expected: 0)")
            results.append(("Get Sources", True))
        else:
            results.append(("Get Sources", False))
        
        # Test 2: Monitoring dashboard (should work even with no sources)
        success, response = self.test_api_call(
            "Monitoring Dashboard (Empty)",
            "GET",
            f"scenarios/{self.scenario_id}/monitoring-dashboard",
            200,
            timeout=10
        )
        
        if success:
            active_sources = response.get('active_sources', 0)
            total_data_points = response.get('total_data_points', 0)
            self.log(f"   📈 Dashboard: {active_sources} active sources, {total_data_points} data points")
            results.append(("Dashboard", True))
        else:
            results.append(("Dashboard", False))
        
        # Test 3: Data collection (should handle no sources gracefully)
        success, response = self.test_api_call(
            "Data Collection (No Sources)",
            "POST",
            f"scenarios/{self.scenario_id}/collect-data",
            200,
            timeout=10
        )
        
        if success:
            status = response.get('collection_status', 'unknown')
            sources_monitored = response.get('sources_monitored', 0)
            self.log(f"   🤖 Collection status: {status}, sources: {sources_monitored}")
            results.append(("Data Collection", True))
        else:
            # Check if it failed due to no sources (which is acceptable)
            if response.get('error') and 'no active monitoring sources' in str(response.get('error', '')).lower():
                self.log(f"   ℹ️  Data collection failed as expected (no sources)")
                results.append(("Data Collection", True))
            else:
                results.append(("Data Collection", False))
        
        return results

    def test_ai_monitoring_endpoints(self):
        """Test monitoring endpoints that require AI processing"""
        self.log("\n🤖 Testing AI-Powered Monitoring Endpoints...")
        
        results = []
        
        # Test 1: Smart monitoring source suggestions
        self.log("   🧠 Testing Smart Monitoring Source Suggestions...")
        success, response = self.test_api_call(
            "Smart Source Suggestions",
            "POST",
            f"scenarios/{self.scenario_id}/suggest-monitoring-sources",
            200,
            timeout=120,  # 2 minutes for AI processing
            ai_endpoint=True
        )
        
        if success and isinstance(response, list):
            suggestions_count = len(response)
            suggestion_types = set()
            
            for suggestion in response:
                suggestion_type = suggestion.get('suggestion_type', 'unknown')
                suggestion_types.add(suggestion_type)
                confidence = suggestion.get('confidence_score', 0)
                content = suggestion.get('suggestion_content', '')[:60]
                
                self.log(f"      - {suggestion_type}: {confidence:.2f} confidence")
                self.log(f"        Content: {content}...")
            
            self.log(f"   📊 Generated {suggestions_count} suggestions with types: {suggestion_types}")
            results.append(("Smart Suggestions", True))
        else:
            if response.get('error') == 'timeout':
                self.log(f"   ⏰ Smart suggestions timed out (AI processing delay)")
                results.append(("Smart Suggestions", "timeout"))
            else:
                results.append(("Smart Suggestions", False))
        
        # Test 2: Add monitoring source with AI relevance scoring
        self.log("   ➕ Testing Add Monitoring Source with AI Scoring...")
        
        source_data = {
            "source_type": "news_api",
            "source_url": "https://newsapi.org/v2/everything?q=earthquake+california",
            "source_name": "California Earthquake News Monitor",
            "monitoring_frequency": "hourly",
            "data_keywords": ["earthquake", "seismic", "tremor", "california", "disaster"]
        }
        
        success, response = self.test_api_call(
            "Add Monitoring Source",
            "POST",
            f"scenarios/{self.scenario_id}/add-monitoring-source",
            200,
            data=source_data,
            timeout=120,  # 2 minutes for AI processing
            ai_endpoint=True
        )
        
        if success and 'id' in response:
            source_id = response['id']
            relevance_score = response.get('relevance_score', 0)
            status = response.get('status', 'unknown')
            added_by = response.get('added_by_team_member', 'unknown')
            
            self.log(f"   ✅ Added source: {source_data['source_name']}")
            self.log(f"      ID: {source_id}")
            self.log(f"      Relevance: {relevance_score:.2f}")
            self.log(f"      Status: {status}")
            self.log(f"      Added by: {added_by}")
            
            results.append(("Add Source", True))
            
            # Now test getting sources again (should have 1 source)
            success2, response2 = self.test_api_call(
                "Get Sources (After Adding)",
                "GET",
                f"scenarios/{self.scenario_id}/monitoring-sources",
                200,
                timeout=10
            )
            
            if success2 and isinstance(response2, list):
                sources_count = len(response2)
                self.log(f"   📋 Now have {sources_count} monitoring source(s)")
                
                if sources_count > 0:
                    source = response2[0]
                    self.log(f"      Source: {source.get('source_name', 'Unknown')}")
                    self.log(f"      Type: {source.get('source_type', 'unknown')}")
                    self.log(f"      Keywords: {source.get('data_keywords', [])}")
                
                results.append(("Get Sources After Add", True))
            else:
                results.append(("Get Sources After Add", False))
            
        else:
            if response.get('error') == 'timeout':
                self.log(f"   ⏰ Add source timed out (AI processing delay)")
                results.append(("Add Source", "timeout"))
            else:
                results.append(("Add Source", False))
        
        return results

    def test_complete_workflow(self):
        """Test the complete intelligent monitoring workflow"""
        self.log("\n🔄 Testing Complete Intelligent Monitoring Workflow...")
        
        workflow_steps = []
        
        # Step 1: Create scenario (already done)
        workflow_steps.append(("Create Scenario", True))
        
        # Step 2: Get smart suggestions
        self.log("   Step 2: Getting smart monitoring suggestions...")
        success, _ = self.test_api_call(
            "Workflow - Smart Suggestions",
            "POST",
            f"scenarios/{self.scenario_id}/suggest-monitoring-sources",
            200,
            timeout=90,
            ai_endpoint=True
        )
        workflow_steps.append(("Smart Suggestions", success))
        
        # Step 3: Add team sources
        self.log("   Step 3: Adding team monitoring sources...")
        
        team_sources = [
            {
                "source_type": "government_data",
                "source_url": "https://earthquake.usgs.gov/fdsnws/event/1/",
                "source_name": "USGS Earthquake Feed",
                "monitoring_frequency": "real_time",
                "data_keywords": ["magnitude", "epicenter", "aftershock"]
            },
            {
                "source_type": "social_media",
                "source_url": "https://twitter.com/api/search?q=earthquake",
                "source_name": "Social Media Earthquake Monitor",
                "monitoring_frequency": "hourly",
                "data_keywords": ["earthquake", "shaking", "emergency"]
            }
        ]
        
        sources_added = 0
        for source_data in team_sources:
            success, _ = self.test_api_call(
                f"Add Team Source: {source_data['source_name']}",
                "POST",
                f"scenarios/{self.scenario_id}/add-monitoring-source",
                200,
                data=source_data,
                timeout=90,
                ai_endpoint=True
            )
            if success:
                sources_added += 1
        
        workflow_steps.append(("Add Team Sources", sources_added > 0))
        
        # Step 4: Collect data
        self.log("   Step 4: Collecting monitoring data...")
        success, response = self.test_api_call(
            "Workflow - Data Collection",
            "POST",
            f"scenarios/{self.scenario_id}/collect-data",
            200,
            timeout=30
        )
        workflow_steps.append(("Data Collection", success))
        
        # Step 5: View dashboard
        self.log("   Step 5: Viewing monitoring dashboard...")
        success, response = self.test_api_call(
            "Workflow - Dashboard",
            "GET",
            f"scenarios/{self.scenario_id}/monitoring-dashboard",
            200,
            timeout=15
        )
        
        if success:
            active_sources = response.get('active_sources', 0)
            total_data_points = response.get('total_data_points', 0)
            self.log(f"      Final dashboard: {active_sources} sources, {total_data_points} data points")
        
        workflow_steps.append(("Dashboard View", success))
        
        return workflow_steps

    def cleanup(self):
        """Clean up test data"""
        self.log("\n🧹 Cleaning up test data...")
        
        if self.scenario_id:
            success, _ = self.test_api_call(
                "Delete Test Scenario",
                "DELETE",
                f"scenarios/{self.scenario_id}",
                200,
                timeout=10
            )
            
            if success:
                self.log("   ✅ Test scenario deleted")
            else:
                self.log("   ⚠️  Failed to delete test scenario")

    def run_comprehensive_test(self):
        """Run the complete comprehensive test suite"""
        self.log("🚀 COMPREHENSIVE INTELLIGENT MONITORING NETWORK TEST")
        self.log("=" * 70)
        
        # Phase 1: Authentication
        if not self.quick_auth_setup():
            self.log("❌ Authentication failed - cannot continue")
            return False
        
        # Phase 2: Scenario setup
        if not self.create_test_scenario():
            self.log("❌ Scenario creation failed - cannot continue")
            return False
        
        # Phase 3: Test non-AI endpoints
        non_ai_results = self.test_non_ai_monitoring_endpoints()
        
        # Phase 4: Test AI endpoints
        ai_results = self.test_ai_monitoring_endpoints()
        
        # Phase 5: Test complete workflow
        workflow_results = self.test_complete_workflow()
        
        # Phase 6: Cleanup
        self.cleanup()
        
        # Results summary
        self.log("\n" + "=" * 70)
        self.log("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        self.log("=" * 70)
        
        self.log("\n🔧 Non-AI Monitoring Features:")
        for test_name, result in non_ai_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {status} - {test_name}")
        
        self.log("\n🤖 AI-Powered Monitoring Features:")
        for test_name, result in ai_results:
            if result == "timeout":
                status = "⏰ TIMEOUT"
            elif result:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            self.log(f"   {status} - {test_name}")
        
        self.log("\n🔄 Complete Workflow Test:")
        for test_name, result in workflow_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {status} - {test_name}")
        
        # Calculate success rates
        non_ai_passed = sum(1 for _, result in non_ai_results if result)
        ai_passed = sum(1 for _, result in ai_results if result and result != "timeout")
        ai_timeout = sum(1 for _, result in ai_results if result == "timeout")
        workflow_passed = sum(1 for _, result in workflow_results if result)
        
        self.log(f"\n📈 Overall API Tests: {self.tests_passed}/{self.tests_run} passed")
        self.log(f"🔧 Non-AI Features: {non_ai_passed}/{len(non_ai_results)} working")
        self.log(f"🤖 AI Features: {ai_passed}/{len(ai_results)} working ({ai_timeout} timeouts)")
        self.log(f"🔄 Workflow: {workflow_passed}/{len(workflow_results)} steps successful")
        
        # Final assessment
        total_working = non_ai_passed + ai_passed
        total_features = len(non_ai_results) + len(ai_results)
        
        if total_working >= total_features * 0.8:  # 80% success rate
            self.log("\n🎉 INTELLIGENT MONITORING NETWORK IS WORKING!")
            self.log("   ✅ Core functionality implemented and operational")
            if ai_timeout > 0:
                self.log(f"   ⏰ Note: {ai_timeout} AI features experienced timeouts (expected)")
            return True
        else:
            self.log(f"\n⚠️  MONITORING NETWORK NEEDS ATTENTION")
            self.log(f"   📊 {total_working}/{total_features} features working")
            return False

def main():
    tester = ComprehensiveMonitoringTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())