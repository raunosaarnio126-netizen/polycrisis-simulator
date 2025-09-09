#!/usr/bin/env python3
"""
Focused test for Intelligent Monitoring Network features
"""
import requests
import json
import sys
from datetime import datetime

class MonitoringNetworkTester:
    def __init__(self):
        self.base_url = "https://crisis-monitor-3.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.scenario_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def test_api_call(self, name, method, endpoint, expected_status, data=None):
        """Make API call and check response"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}")
                except:
                    self.log(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}")
            return False, {}

    def setup_test_environment(self):
        """Setup user and scenario for testing"""
        self.log("🚀 Setting up test environment...")
        
        # Register user
        user_data = {
            "email": f"monitor_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"monitor_test_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Monitoring Test Org"
        }
        
        success, response = self.test_api_call(
            "User Registration", "POST", "register", 200, user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.log(f"   ✅ User registered and token obtained")
        else:
            self.log("   ❌ Failed to register user")
            return False

        # Create test scenario
        scenario_data = {
            "title": "Monitoring Test Earthquake Scenario",
            "description": "Test scenario for intelligent monitoring network features",
            "crisis_type": "natural_disaster",
            "severity_level": 7,
            "affected_regions": ["California", "Nevada"],
            "key_variables": ["seismic activity", "population density", "infrastructure"]
        }
        
        success, response = self.test_api_call(
            "Create Test Scenario", "POST", "scenarios", 200, scenario_data
        )
        
        if success and 'id' in response:
            self.scenario_id = response['id']
            self.log(f"   ✅ Test scenario created: {self.scenario_id}")
            return True
        else:
            self.log("   ❌ Failed to create test scenario")
            return False

    def test_smart_monitoring_suggestions(self):
        """Test Smart Monitoring Source Suggestions"""
        self.log("\n🧠 Testing Smart Monitoring Source Suggestions...")
        
        success, response = self.test_api_call(
            "Smart Source Suggestions",
            "POST",
            f"scenarios/{self.scenario_id}/suggest-monitoring-sources",
            200
        )
        
        if success and isinstance(response, list):
            self.log(f"   📊 Generated {len(response)} smart suggestions")
            
            suggestion_types = set()
            for suggestion in response:
                suggestion_type = suggestion.get('suggestion_type', 'unknown')
                suggestion_types.add(suggestion_type)
                confidence = suggestion.get('confidence_score', 0)
                content = suggestion.get('suggestion_content', '')[:80]
                reasoning = suggestion.get('reasoning', '')[:80]
                
                self.log(f"   - {suggestion_type}: {confidence:.2f} confidence")
                self.log(f"     Content: {content}...")
                self.log(f"     Reasoning: {reasoning}...")
            
            self.log(f"   📈 Suggestion types found: {suggestion_types}")
            
            # Check for expected types
            expected_types = {'data_source', 'monitoring_keyword', 'analysis_focus'}
            found_types = suggestion_types.intersection(expected_types)
            self.log(f"   ✅ Expected types found: {found_types}")
            
            return len(found_types) > 0
        else:
            self.log("   ❌ No suggestions generated or invalid response")
            return False

    def test_team_collaboration_sources(self):
        """Test Team Collaboration - Adding Monitoring Sources"""
        self.log("\n👥 Testing Team Collaboration - Add Monitoring Sources...")
        
        test_sources = [
            {
                "source_type": "news_api",
                "source_url": "https://newsapi.org/v2/everything?q=earthquake",
                "source_name": "Earthquake News Monitor",
                "monitoring_frequency": "hourly",
                "data_keywords": ["earthquake", "seismic", "tremor", "disaster"]
            },
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
                "monitoring_frequency": "daily",
                "data_keywords": ["earthquake", "shaking", "emergency"]
            }
        ]
        
        added_sources = 0
        source_ids = []
        
        for i, source_data in enumerate(test_sources):
            success, response = self.test_api_call(
                f"Add Source {i+1}: {source_data['source_name']}",
                "POST",
                f"scenarios/{self.scenario_id}/add-monitoring-source",
                200,
                source_data
            )
            
            if success and 'id' in response:
                added_sources += 1
                source_ids.append(response['id'])
                relevance = response.get('relevance_score', 0)
                status = response.get('status', 'unknown')
                added_by = response.get('added_by_team_member', 'unknown')
                
                self.log(f"   ✅ Added {source_data['source_name']}")
                self.log(f"      Relevance: {relevance:.2f}, Status: {status}, Added by: {added_by}")
            else:
                self.log(f"   ❌ Failed to add {source_data['source_name']}")
        
        self.log(f"   📊 Successfully added {added_sources}/{len(test_sources)} sources")
        return added_sources > 0, source_ids

    def test_get_monitoring_sources(self):
        """Test Getting Monitoring Sources"""
        self.log("\n📋 Testing Get Monitoring Sources...")
        
        success, response = self.test_api_call(
            "Get Monitoring Sources",
            "GET",
            f"scenarios/{self.scenario_id}/monitoring-sources",
            200
        )
        
        if success and isinstance(response, list):
            self.log(f"   📊 Found {len(response)} monitoring sources")
            
            for source in response:
                name = source.get('source_name', 'Unknown')
                source_type = source.get('source_type', 'unknown')
                status = source.get('status', 'unknown')
                relevance = source.get('relevance_score', 0)
                frequency = source.get('monitoring_frequency', 'unknown')
                keywords = source.get('data_keywords', [])
                
                self.log(f"   - {name} ({source_type})")
                self.log(f"     Status: {status}, Relevance: {relevance:.2f}, Frequency: {frequency}")
                self.log(f"     Keywords: {keywords}")
            
            return len(response) > 0
        else:
            self.log("   ❌ No sources found or invalid response")
            return False

    def test_automated_data_collection(self):
        """Test Automated Data Collection System"""
        self.log("\n🤖 Testing Automated Data Collection...")
        
        success, response = self.test_api_call(
            "Collect Monitoring Data",
            "POST",
            f"scenarios/{self.scenario_id}/collect-data",
            200
        )
        
        if success:
            sources_monitored = response.get('sources_monitored', 0)
            data_points = response.get('data_points_collected', 0)
            status = response.get('collection_status', 'unknown')
            
            self.log(f"   📊 Collection Results:")
            self.log(f"      Sources monitored: {sources_monitored}")
            self.log(f"      Data points collected: {data_points}")
            self.log(f"      Collection status: {status}")
            
            # Check collected data details
            collected_data = response.get('collected_data', [])
            if collected_data:
                self.log(f"   📋 Sample collected data ({len(collected_data)} items):")
                for i, item in enumerate(collected_data[:3]):  # Show first 3
                    title = item.get('data_title', 'No title')
                    relevance = item.get('relevance_score', 0)
                    sentiment = item.get('sentiment_score', 0)
                    urgency = item.get('urgency_level', 'unknown')
                    keywords = item.get('keywords_matched', [])
                    
                    self.log(f"      {i+1}. {title}")
                    self.log(f"         Relevance: {relevance:.2f}, Sentiment: {sentiment:.2f}")
                    self.log(f"         Urgency: {urgency}, Keywords: {keywords}")
            
            return sources_monitored > 0
        else:
            self.log("   ❌ Data collection failed")
            return False

    def test_monitoring_dashboard(self):
        """Test Monitoring Dashboard & Analytics"""
        self.log("\n📊 Testing Monitoring Dashboard & Analytics...")
        
        success, response = self.test_api_call(
            "Monitoring Dashboard",
            "GET",
            f"scenarios/{self.scenario_id}/monitoring-dashboard",
            200
        )
        
        if success:
            active_sources = response.get('active_sources', 0)
            total_data_points = response.get('total_data_points', 0)
            avg_relevance = response.get('average_relevance_score', 0)
            insights_count = response.get('recent_insights_count', 0)
            collection_status = response.get('data_collection_status', 'unknown')
            
            self.log(f"   📈 Dashboard Metrics:")
            self.log(f"      Active sources: {active_sources}")
            self.log(f"      Total data points: {total_data_points}")
            self.log(f"      Average relevance: {avg_relevance:.2f}")
            self.log(f"      Recent insights: {insights_count}")
            self.log(f"      Collection status: {collection_status}")
            
            # Source status breakdown
            source_status = response.get('source_status_breakdown', {})
            if source_status:
                self.log(f"   📊 Source Status Breakdown:")
                for status, count in source_status.items():
                    self.log(f"      {status}: {count}")
            
            # Urgency distribution
            urgency_dist = response.get('urgency_level_distribution', {})
            if urgency_dist:
                self.log(f"   ⚠️  Urgency Level Distribution:")
                for level, count in urgency_dist.items():
                    self.log(f"      {level}: {count}")
            
            # Recent insights
            recent_insights = response.get('recent_insights', [])
            if recent_insights:
                self.log(f"   💡 Recent Insights (showing first 3):")
                for i, insight in enumerate(recent_insights[:3]):
                    summary = insight.get('insight_summary', 'No summary')
                    self.log(f"      {i+1}. {summary}")
            
            return active_sources >= 0  # Dashboard should return even if no sources
        else:
            self.log("   ❌ Dashboard access failed")
            return False

    def test_complete_workflow(self):
        """Test Complete Intelligent Monitoring Workflow"""
        self.log("\n🔄 Testing Complete Intelligent Monitoring Workflow...")
        
        workflow_steps = [
            ("Smart Suggestions", self.test_smart_monitoring_suggestions),
            ("Team Sources", lambda: self.test_team_collaboration_sources()[0]),
            ("Get Sources", self.test_get_monitoring_sources),
            ("Data Collection", self.test_automated_data_collection),
            ("Dashboard Analytics", self.test_monitoring_dashboard)
        ]
        
        workflow_success = 0
        for step_name, step_func in workflow_steps:
            self.log(f"   🔸 Workflow Step: {step_name}")
            if step_func():
                workflow_success += 1
                self.log(f"      ✅ {step_name} completed successfully")
            else:
                self.log(f"      ❌ {step_name} failed")
        
        self.log(f"   📊 Workflow Completion: {workflow_success}/{len(workflow_steps)} steps successful")
        return workflow_success == len(workflow_steps)

    def cleanup(self):
        """Clean up test data"""
        self.log("\n🧹 Cleaning up test data...")
        
        if self.scenario_id:
            success, _ = self.test_api_call(
                "Delete Test Scenario",
                "DELETE",
                f"scenarios/{self.scenario_id}",
                200
            )
            
            if success:
                self.log("   ✅ Test scenario deleted")
            else:
                self.log("   ⚠️  Failed to delete test scenario")

    def run_all_tests(self):
        """Run all monitoring network tests"""
        self.log("🚀 Starting Intelligent Monitoring Network Tests")
        self.log("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            self.log("❌ Failed to setup test environment")
            return False
        
        # Individual feature tests
        test_results = []
        
        test_results.append(("Smart Suggestions", self.test_smart_monitoring_suggestions()))
        
        sources_success, source_ids = self.test_team_collaboration_sources()
        test_results.append(("Team Collaboration", sources_success))
        
        test_results.append(("Get Sources", self.test_get_monitoring_sources()))
        test_results.append(("Data Collection", self.test_automated_data_collection()))
        test_results.append(("Dashboard", self.test_monitoring_dashboard()))
        
        # Complete workflow test
        test_results.append(("Complete Workflow", self.test_complete_workflow()))
        
        # Cleanup
        self.cleanup()
        
        # Results summary
        self.log("\n" + "=" * 60)
        self.log("📊 INTELLIGENT MONITORING NETWORK TEST RESULTS")
        self.log("=" * 60)
        
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} - {test_name}")
            if result:
                passed_tests += 1
        
        self.log(f"\n📈 Overall API Tests: {self.tests_passed}/{self.tests_run} passed")
        self.log(f"🎯 Feature Tests: {passed_tests}/{len(test_results)} passed")
        
        if passed_tests == len(test_results):
            self.log("🎉 ALL INTELLIGENT MONITORING NETWORK FEATURES WORKING!")
            return True
        else:
            self.log(f"⚠️  {len(test_results) - passed_tests} features need attention")
            return False

def main():
    tester = MonitoringNetworkTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())