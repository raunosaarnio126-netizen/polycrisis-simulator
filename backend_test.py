import requests
import sys
import json
from datetime import datetime

class PolycrisisAPITester:
    def __init__(self, base_url="https://polycrisis-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_scenario_id = None
        self.monitoring_source_id = None

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

    def test_user_registration(self):
        """Test enhanced user registration with enterprise fields"""
        test_user_data = {
            "email": f"test_user_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Test Organization",
            "job_title": "Crisis Management Director",
            "department": "Risk Management"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
            return True, test_user_data
        return False, {}

    def test_user_login(self, user_data):
        """Test user login"""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Login token: {self.token[:20]}...")
            return True
        return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "me",
            200
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
            return True
        return False

    def test_create_scenario(self):
        """Test creating a crisis scenario"""
        scenario_data = {
            "title": "Test Earthquake Scenario",
            "description": "A major earthquake hitting a metropolitan area with cascading effects on infrastructure and population.",
            "crisis_type": "natural_disaster",
            "severity_level": 8,
            "affected_regions": ["California", "San Francisco Bay Area"],
            "key_variables": ["Population density", "Infrastructure age", "Emergency response capacity"]
        }
        
        success, response = self.run_test(
            "Create Scenario",
            "POST",
            "scenarios",
            200,
            data=scenario_data
        )
        
        if success and 'id' in response:
            self.created_scenario_id = response['id']
            print(f"   Created scenario ID: {self.created_scenario_id}")
            return True
        return False

    def test_get_scenarios(self):
        """Test getting user scenarios"""
        success, response = self.run_test(
            "Get Scenarios",
            "GET",
            "scenarios",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} scenarios")
            return True
        return False

    def test_get_single_scenario(self):
        """Test getting a single scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Single Scenario",
            "GET",
            f"scenarios/{self.created_scenario_id}",
            200
        )
        
        return success and 'id' in response

    def test_ai_genie(self):
        """Test AI Genie functionality"""
        ai_request = {
            "scenario_id": self.created_scenario_id,
            "user_query": "What are the key risks and mitigation strategies for this earthquake scenario?",
            "context": "Testing AI Genie functionality"
        }
        
        success, response = self.run_test(
            "AI Genie Chat",
            "POST",
            "ai-genie",
            200,
            data=ai_request
        )
        
        if success and 'response' in response:
            print(f"   AI Response length: {len(response.get('response', ''))}")
            print(f"   Suggestions count: {len(response.get('suggestions', []))}")
            print(f"   Monitoring tasks count: {len(response.get('monitoring_tasks', []))}")
            return True
        return False

    def test_run_simulation(self):
        """Test running simulation on scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for simulation")
            return False
            
        success, response = self.run_test(
            "Run Simulation",
            "POST",
            f"scenarios/{self.created_scenario_id}/simulate",
            200
        )
        
        if success and 'analysis' in response:
            print(f"   Analysis length: {len(response.get('analysis', ''))}")
            print(f"   Confidence score: {response.get('confidence_score', 'N/A')}")
            return True
        return False

    def test_delete_scenario(self):
        """Test deleting a scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for deletion")
            return False
            
        success, response = self.run_test(
            "Delete Scenario",
            "DELETE",
            f"scenarios/{self.created_scenario_id}",
            200
        )
        
        if success:
            print(f"   Scenario deleted successfully")
            # Verify scenario is actually deleted by trying to get it
            verify_success, verify_response = self.run_test(
                "Verify Scenario Deletion",
                "GET",
                f"scenarios/{self.created_scenario_id}",
                404
            )
            return verify_success
        return False

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            print(f"   Total scenarios: {response.get('total_scenarios', 'N/A')}")
            print(f"   Active scenarios: {response.get('active_scenarios', 'N/A')}")
            print(f"   Total simulations: {response.get('total_simulations', 'N/A')}")
            print(f"   Organization: {response.get('user_organization', 'N/A')}")
            return True
        return False

    def test_generate_game_book(self):
        """Test Game Book generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Game Book generation")
            return False
            
        success, response = self.run_test(
            "Generate Game Book",
            "POST",
            f"scenarios/{self.created_scenario_id}/game-book",
            200
        )
        
        if success and 'game_book_content' in response:
            print(f"   Game Book content length: {len(response.get('game_book_content', ''))}")
            print(f"   Decision points: {len(response.get('decision_points', []))}")
            print(f"   Resource requirements: {len(response.get('resource_requirements', []))}")
            print(f"   Timeline phases: {len(response.get('timeline_phases', []))}")
            print(f"   Success metrics: {len(response.get('success_metrics', []))}")
            return True
        return False

    def test_generate_action_plan(self):
        """Test Action Plan generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Action Plan generation")
            return False
            
        success, response = self.run_test(
            "Generate Action Plan",
            "POST",
            f"scenarios/{self.created_scenario_id}/action-plan",
            200
        )
        
        if success and 'immediate_actions' in response:
            print(f"   Immediate actions: {len(response.get('immediate_actions', []))}")
            print(f"   Short-term actions: {len(response.get('short_term_actions', []))}")
            print(f"   Long-term actions: {len(response.get('long_term_actions', []))}")
            print(f"   Responsible parties: {len(response.get('responsible_parties', []))}")
            print(f"   Priority level: {response.get('priority_level', 'N/A')}")
            return True
        return False

    def test_generate_strategy_implementation(self):
        """Test Strategy Implementation generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Strategy Implementation generation")
            return False
            
        success, response = self.run_test(
            "Generate Strategy Implementation",
            "POST",
            f"scenarios/{self.created_scenario_id}/strategy-implementation",
            200
        )
        
        if success and 'implementation_strategy' in response:
            print(f"   Implementation strategy length: {len(response.get('implementation_strategy', ''))}")
            print(f"   Organizational changes: {len(response.get('organizational_changes', []))}")
            print(f"   Policy recommendations: {len(response.get('policy_recommendations', []))}")
            print(f"   Training requirements: {len(response.get('training_requirements', []))}")
            print(f"   Budget considerations: {len(response.get('budget_considerations', []))}")
            print(f"   Stakeholder engagement: {len(response.get('stakeholder_engagement', []))}")
            return True
        return False

    def test_get_game_book(self):
        """Test retrieving Game Book"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Game Book retrieval")
            return False
            
        success, response = self.run_test(
            "Get Game Book",
            "GET",
            f"scenarios/{self.created_scenario_id}/game-book",
            200
        )
        
        return success and 'game_book_content' in response

    def test_get_action_plan(self):
        """Test retrieving Action Plan"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Action Plan retrieval")
            return False
            
        success, response = self.run_test(
            "Get Action Plan",
            "GET",
            f"scenarios/{self.created_scenario_id}/action-plan",
            200
        )
        
        return success and 'immediate_actions' in response

    def test_get_strategy_implementation(self):
        """Test retrieving Strategy Implementation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Strategy Implementation retrieval")
            return False
            
        success, response = self.run_test(
            "Get Strategy Implementation",
            "GET",
            f"scenarios/{self.created_scenario_id}/strategy-implementation",
            200
        )
        
        return success and 'implementation_strategy' in response

    # ========== ADVANCED FEATURES TESTING ==========
    
    def test_deploy_monitor_agents(self):
        """Test deploying AI Monitor Agents"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Monitor Agents deployment")
            return False
            
        success, response = self.run_test(
            "Deploy AI Monitor Agents",
            "POST",
            f"scenarios/{self.created_scenario_id}/deploy-monitors",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Deployed {len(response)} monitor agents")
            agent_types = [agent.get('agent_type') for agent in response]
            print(f"   Agent types: {agent_types}")
            
            # Verify all 4 expected agent types are present
            expected_types = ['risk_monitor', 'performance_tracker', 'anomaly_detector', 'trend_analyzer']
            for expected_type in expected_types:
                if expected_type in agent_types:
                    print(f"   ✅ {expected_type} agent deployed")
                else:
                    print(f"   ❌ {expected_type} agent missing")
                    return False
            return True
        return False

    def test_get_monitor_agents(self):
        """Test retrieving Monitor Agents"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Monitor Agents retrieval")
            return False
            
        success, response = self.run_test(
            "Get Monitor Agents",
            "GET",
            f"scenarios/{self.created_scenario_id}/monitor-agents",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} monitor agents")
            for agent in response:
                print(f"   - {agent.get('agent_type')}: {agent.get('status')} (Risk: {agent.get('risk_level')})")
            return True
        return False

    def test_complex_systems_analysis(self):
        """Test Complex Adaptive Systems Analysis"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Complex Systems Analysis")
            return False
            
        success, response = self.run_test(
            "Complex Adaptive Systems Analysis",
            "POST",
            f"scenarios/{self.created_scenario_id}/complex-systems-analysis",
            200
        )
        
        if success and 'system_components' in response:
            print(f"   System components: {len(response.get('system_components', []))}")
            print(f"   Interconnections: {len(response.get('interconnections', []))}")
            print(f"   Feedback loops: {len(response.get('feedback_loops', []))}")
            print(f"   Emergent behaviors: {len(response.get('emergent_behaviors', []))}")
            print(f"   Adaptation mechanisms: {len(response.get('adaptation_mechanisms', []))}")
            print(f"   Tipping points: {len(response.get('tipping_points', []))}")
            print(f"   System dynamics length: {len(response.get('system_dynamics', ''))}")
            return True
        return False

    def test_generate_system_metrics(self):
        """Test System Metrics Generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for System Metrics generation")
            return False
            
        success, response = self.run_test(
            "Generate System Metrics",
            "POST",
            f"scenarios/{self.created_scenario_id}/generate-metrics",
            200
        )
        
        if success and 'resilience_score' in response:
            print(f"   Resilience score: {response.get('resilience_score', 'N/A')}")
            print(f"   Complexity index: {response.get('complexity_index', 'N/A')}")
            print(f"   Cascading risk factor: {response.get('cascading_risk_factor', 'N/A')}")
            print(f"   Intervention effectiveness: {response.get('intervention_effectiveness', 'N/A')}")
            print(f"   System stability: {response.get('system_stability', 'N/A')}")
            print(f"   Adaptive capacity: {response.get('adaptive_capacity', 'N/A')}")
            print(f"   Interconnectedness level: {response.get('interconnectedness_level', 'N/A')}")
            return True
        return False

    def test_generate_learning_insights(self):
        """Test Adaptive Learning Insights Generation"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for Learning Insights generation")
            return False
            
        success, response = self.run_test(
            "Generate Learning Insights",
            "POST",
            f"scenarios/{self.created_scenario_id}/generate-learning-insights",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Generated {len(response)} learning insights")
            insight_types = [insight.get('insight_type') for insight in response]
            print(f"   Insight types: {insight_types}")
            
            # Check for expected insight types
            expected_types = ['pattern_recognition', 'outcome_prediction', 'optimization_suggestion']
            for expected_type in expected_types:
                if expected_type in insight_types:
                    print(f"   ✅ {expected_type} insight generated")
                else:
                    print(f"   ❌ {expected_type} insight missing")
            
            # Show confidence scores
            for insight in response:
                print(f"   - {insight.get('insight_type')}: Confidence {insight.get('confidence_score', 'N/A')}")
            return True
        return False

    def test_advanced_analytics_dashboard(self):
        """Test Advanced Analytics Dashboard"""
        success, response = self.run_test(
            "Advanced Analytics Dashboard",
            "GET",
            "dashboard/advanced-analytics",
            200
        )
        
        if success:
            print(f"   Total scenarios: {response.get('total_scenarios', 'N/A')}")
            print(f"   Active scenarios: {response.get('active_scenarios', 'N/A')}")
            print(f"   Total simulations: {response.get('total_simulations', 'N/A')}")
            print(f"   Total monitor agents: {response.get('total_monitor_agents', 'N/A')}")
            print(f"   Learning insights generated: {response.get('learning_insights_generated', 'N/A')}")
            print(f"   Average resilience score: {response.get('average_resilience_score', 'N/A')}")
            print(f"   System health score: {response.get('system_health_score', 'N/A')}")
            print(f"   Adaptive learning active: {response.get('adaptive_learning_active', 'N/A')}")
            print(f"   Complex systems analyzed: {response.get('complex_systems_analyzed', 'N/A')}")
            print(f"   Monitoring coverage: {response.get('monitoring_coverage', 'N/A')}")
            return True
        return False

    # ========== INTELLIGENT MONITORING NETWORK TESTING ==========
    
    def test_suggest_monitoring_sources(self):
        """Test Smart Monitoring Source Suggestions"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for monitoring source suggestions")
            return False
            
        success, response = self.run_test(
            "Smart Monitoring Source Suggestions",
            "POST",
            f"scenarios/{self.created_scenario_id}/suggest-monitoring-sources",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Generated {len(response)} smart suggestions")
            suggestion_types = [suggestion.get('suggestion_type') for suggestion in response]
            print(f"   Suggestion types: {set(suggestion_types)}")
            
            # Check for expected suggestion types
            expected_types = ['data_source', 'monitoring_keyword', 'analysis_focus']
            for suggestion in response:
                suggestion_type = suggestion.get('suggestion_type')
                confidence = suggestion.get('confidence_score', 0)
                content = suggestion.get('suggestion_content', '')[:100]
                reasoning = suggestion.get('reasoning', '')[:100]
                print(f"   - {suggestion_type}: {confidence:.2f} confidence")
                print(f"     Content: {content}...")
                print(f"     Reasoning: {reasoning}...")
            return True
        return False

    def test_add_monitoring_source(self):
        """Test Team Collaboration - Add Monitoring Source"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for adding monitoring source")
            return False
            
        source_data = {
            "source_type": "news_api",
            "source_url": "https://newsapi.org/v2/everything?q=earthquake",
            "source_name": "Earthquake News Monitor",
            "monitoring_frequency": "hourly",
            "data_keywords": ["earthquake", "seismic activity", "disaster response", "emergency"]
        }
        
        success, response = self.run_test(
            "Add Monitoring Source",
            "POST",
            f"scenarios/{self.created_scenario_id}/add-monitoring-source",
            200,
            data=source_data
        )
        
        if success and 'id' in response:
            self.monitoring_source_id = response['id']
            print(f"   Created monitoring source ID: {self.monitoring_source_id}")
            print(f"   Source type: {response.get('source_type', 'N/A')}")
            print(f"   Source name: {response.get('source_name', 'N/A')}")
            print(f"   Relevance score: {response.get('relevance_score', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Monitoring frequency: {response.get('monitoring_frequency', 'N/A')}")
            print(f"   Keywords: {response.get('data_keywords', [])}")
            print(f"   Added by: {response.get('added_by_team_member', 'N/A')}")
            return True
        return False

    def test_get_monitoring_sources(self):
        """Test Get Monitoring Sources for Scenario"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for getting monitoring sources")
            return False
            
        success, response = self.run_test(
            "Get Monitoring Sources",
            "GET",
            f"scenarios/{self.created_scenario_id}/monitoring-sources",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} monitoring sources")
            for source in response:
                print(f"   - {source.get('source_name')}: {source.get('source_type')} ({source.get('status')})")
                print(f"     Relevance: {source.get('relevance_score', 'N/A')}, Frequency: {source.get('monitoring_frequency', 'N/A')}")
            return True
        return False

    def test_collect_monitoring_data(self):
        """Test Automated Data Collection System"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for data collection")
            return False
            
        success, response = self.run_test(
            "Collect Monitoring Data",
            "POST",
            f"scenarios/{self.created_scenario_id}/collect-data",
            200
        )
        
        if success:
            print(f"   Sources monitored: {response.get('sources_monitored', 'N/A')}")
            print(f"   Data points collected: {response.get('data_points_collected', 'N/A')}")
            print(f"   Collection status: {response.get('collection_status', 'N/A')}")
            
            # Check collected data details if available
            collected_data = response.get('collected_data', [])
            if collected_data:
                print(f"   Sample collected data items: {len(collected_data)}")
                for item in collected_data[:3]:  # Show first 3 items
                    print(f"   - Title: {item.get('data_title', 'N/A')}")
                    print(f"     Relevance: {item.get('relevance_score', 'N/A')}")
                    print(f"     Sentiment: {item.get('sentiment_score', 'N/A')}")
                    print(f"     Urgency: {item.get('urgency_level', 'N/A')}")
                    print(f"     Keywords matched: {item.get('keywords_matched', [])}")
            return True
        return False

    def test_monitoring_dashboard(self):
        """Test Monitoring Dashboard & Analytics"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for monitoring dashboard")
            return False
            
        success, response = self.run_test(
            "Monitoring Dashboard",
            "GET",
            f"scenarios/{self.created_scenario_id}/monitoring-dashboard",
            200
        )
        
        if success:
            print(f"   Active sources: {response.get('active_sources', 'N/A')}")
            print(f"   Total data points: {response.get('total_data_points', 'N/A')}")
            print(f"   Average relevance score: {response.get('average_relevance_score', 'N/A')}")
            print(f"   Recent insights count: {response.get('recent_insights_count', 'N/A')}")
            print(f"   Data collection status: {response.get('data_collection_status', 'N/A')}")
            
            # Check source status breakdown
            source_status = response.get('source_status_breakdown', {})
            if source_status:
                print(f"   Source status breakdown:")
                for status, count in source_status.items():
                    print(f"     {status}: {count}")
            
            # Check urgency level distribution
            urgency_distribution = response.get('urgency_level_distribution', {})
            if urgency_distribution:
                print(f"   Urgency level distribution:")
                for level, count in urgency_distribution.items():
                    print(f"     {level}: {count}")
            
            # Check recent insights
            recent_insights = response.get('recent_insights', [])
            if recent_insights:
                print(f"   Recent insights (showing first 3):")
                for insight in recent_insights[:3]:
                    print(f"   - {insight.get('insight_summary', 'N/A')}")
            
            return True
        return False

    def test_team_collaboration_features(self):
        """Test Team Collaboration Features"""
        if not self.created_scenario_id:
            print("❌ No scenario ID available for team collaboration testing")
            return False
        
        # Test adding multiple sources from different team members
        sources_data = [
            {
                "source_type": "social_media",
                "source_url": "https://twitter.com/api/search?q=earthquake",
                "source_name": "Twitter Earthquake Monitor",
                "monitoring_frequency": "real_time",
                "data_keywords": ["earthquake", "tremor", "seismic"]
            },
            {
                "source_type": "government_data",
                "source_url": "https://earthquake.usgs.gov/fdsnws/event/1/",
                "source_name": "USGS Earthquake Data",
                "monitoring_frequency": "hourly",
                "data_keywords": ["magnitude", "epicenter", "aftershock"]
            },
            {
                "source_type": "weather_api",
                "source_url": "https://api.weather.gov/alerts",
                "source_name": "Weather Service Alerts",
                "monitoring_frequency": "daily",
                "data_keywords": ["weather alert", "emergency", "warning"]
            }
        ]
        
        added_sources = 0
        for i, source_data in enumerate(sources_data):
            success, response = self.run_test(
                f"Add Team Source {i+1}",
                "POST",
                f"scenarios/{self.created_scenario_id}/add-monitoring-source",
                200,
                data=source_data
            )
            
            if success:
                added_sources += 1
                print(f"   ✅ Added {source_data['source_name']} (Relevance: {response.get('relevance_score', 'N/A')})")
            else:
                print(f"   ❌ Failed to add {source_data['source_name']}")
        
        print(f"   Successfully added {added_sources}/{len(sources_data)} team sources")
        return added_sources > 0

def main():
    print("🚀 Starting Polycrisis Simulator API Tests")
    print("=" * 50)
    
    tester = PolycrisisAPITester()
    
    # Test sequence
    print("\n📝 Testing Authentication Flow...")
    success, user_data = tester.test_user_registration()
    if not success:
        print("❌ Registration failed, stopping tests")
        return 1

    if not tester.test_user_login(user_data):
        print("❌ Login failed, stopping tests")
        return 1

    if not tester.test_get_user_profile():
        print("❌ Profile fetch failed, stopping tests")
        return 1

    print("\n🎯 Testing Scenario Management...")
    if not tester.test_create_scenario():
        print("❌ Scenario creation failed")
        
    tester.test_get_scenarios()
    tester.test_get_single_scenario()

    print("\n🤖 Testing AI Integration...")
    tester.test_ai_genie()
    tester.test_run_simulation()

    print("\n📋 Testing Strategic Implementation Features...")
    print("   Testing Game Book generation...")
    tester.test_generate_game_book()
    
    print("   Testing Action Plan generation...")
    tester.test_generate_action_plan()
    
    print("   Testing Strategy Implementation generation...")
    tester.test_generate_strategy_implementation()
    
    print("   Testing retrieval of generated artifacts...")
    tester.test_get_game_book()
    tester.test_get_action_plan()
    tester.test_get_strategy_implementation()

    print("\n🤖 Testing Advanced AI Monitor Agents...")
    print("   Deploying AI Monitor Agents...")
    tester.test_deploy_monitor_agents()
    
    print("   Retrieving Monitor Agents...")
    tester.test_get_monitor_agents()

    print("\n🔬 Testing Complex Adaptive Systems...")
    print("   Running Complex Systems Analysis...")
    tester.test_complex_systems_analysis()

    print("\n📈 Testing System Metrics...")
    print("   Generating System Metrics...")
    tester.test_generate_system_metrics()

    print("\n🧠 Testing Adaptive Learning...")
    print("   Generating Learning Insights...")
    tester.test_generate_learning_insights()

    print("\n📊 Testing Dashboard...")
    print("   Basic Dashboard Stats...")
    tester.test_dashboard_stats()
    
    print("   Advanced Analytics Dashboard...")
    tester.test_advanced_analytics_dashboard()

    print("\n🌐 Testing Intelligent Monitoring Network...")
    print("   Testing Smart Monitoring Source Suggestions...")
    tester.test_suggest_monitoring_sources()
    
    print("   Testing Team Collaboration - Add Monitoring Source...")
    tester.test_add_monitoring_source()
    
    print("   Testing Get Monitoring Sources...")
    tester.test_get_monitoring_sources()
    
    print("   Testing Team Collaboration Features...")
    tester.test_team_collaboration_features()
    
    print("   Testing Automated Data Collection...")
    tester.test_collect_monitoring_data()
    
    print("   Testing Monitoring Dashboard & Analytics...")
    tester.test_monitoring_dashboard()

    print("\n🗑️ Testing Scenario Deletion...")
    tester.test_delete_scenario()

    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())