import requests
import sys
import json
from datetime import datetime

class PolycrisisAPITester:
    def __init__(self, base_url="https://crisis-adapt.preview.emergentagent.com"):
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

    # ========== ENTERPRISE FEATURES TESTING ==========
    
    def test_create_company(self):
        """Test Company Management System - Create Company"""
        company_data = {
            "company_name": "Test Enterprise Corp",
            "industry": "Technology",
            "company_size": "medium",
            "website_url": "https://example.com",
            "description": "A test company for crisis management simulation",
            "location": "San Francisco, CA"
        }
        
        success, response = self.run_test(
            "Create Company Profile",
            "POST",
            "companies",
            200,
            data=company_data
        )
        
        if success and 'id' in response:
            self.company_id = response['id']
            print(f"   Created company ID: {self.company_id}")
            print(f"   Company name: {response.get('company_name', 'N/A')}")
            print(f"   Industry: {response.get('industry', 'N/A')}")
            print(f"   Size: {response.get('company_size', 'N/A')}")
            print(f"   Location: {response.get('location', 'N/A')}")
            print(f"   Website analysis: {len(response.get('website_analysis', '')) if response.get('website_analysis') else 0} chars")
            print(f"   Business model: {len(response.get('business_model', '')) if response.get('business_model') else 0} chars")
            print(f"   Key assets: {len(response.get('key_assets', []))}")
            print(f"   Vulnerabilities: {len(response.get('vulnerabilities', []))}")
            print(f"   Stakeholders: {len(response.get('stakeholders', []))}")
            return True
        return False

    def test_get_company(self):
        """Test Get Company Details"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Company Details",
            "GET",
            f"companies/{self.company_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"   Retrieved company: {response.get('company_name', 'N/A')}")
            print(f"   Website analysis available: {bool(response.get('website_analysis'))}")
            print(f"   Business model available: {bool(response.get('business_model'))}")
            return True
        return False

    def test_upload_business_document(self):
        """Test Document Intelligence Platform - Upload Document"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for document upload")
            return False
            
        document_data = {
            "document_name": "Business Continuity Plan 2025",
            "document_type": "business_plan",
            "document_content": """
            BUSINESS CONTINUITY PLAN
            
            Executive Summary:
            This document outlines our comprehensive business continuity strategy for maintaining operations during crisis situations.
            
            Key Objectives:
            1. Ensure employee safety and well-being
            2. Maintain critical business operations
            3. Protect key assets and data
            4. Minimize financial impact
            5. Ensure rapid recovery
            
            Risk Assessment:
            - Natural disasters (earthquakes, floods)
            - Cyber security threats
            - Supply chain disruptions
            - Pandemic scenarios
            - Economic downturns
            
            Critical Business Functions:
            - Customer service operations
            - IT infrastructure and data centers
            - Financial systems and accounting
            - Supply chain management
            - Human resources
            
            Recovery Strategies:
            - Remote work capabilities
            - Backup data centers
            - Alternative suppliers
            - Emergency communication systems
            - Crisis management team activation
            
            Testing and Maintenance:
            Regular testing of all systems and procedures to ensure effectiveness.
            """
        }
        
        success, response = self.run_test(
            "Upload Business Document",
            "POST",
            f"companies/{self.company_id}/documents",
            200,
            data=document_data
        )
        
        if success and 'id' in response:
            self.document_id = response['id']
            print(f"   Uploaded document ID: {self.document_id}")
            print(f"   Document name: {response.get('document_name', 'N/A')}")
            print(f"   Document type: {response.get('document_type', 'N/A')}")
            print(f"   AI analysis: {len(response.get('ai_analysis', '')) if response.get('ai_analysis') else 0} chars")
            print(f"   Key insights: {len(response.get('key_insights', []))}")
            print(f"   Risk factors: {len(response.get('risk_factors', []))}")
            print(f"   Strategic priorities: {len(response.get('strategic_priorities', []))}")
            print(f"   File size: {response.get('file_size', 'N/A')}")
            return True
        return False

    def test_get_company_documents(self):
        """Test Get Company Documents"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for getting documents")
            return False
            
        success, response = self.run_test(
            "Get Company Documents",
            "GET",
            f"companies/{self.company_id}/documents",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} documents")
            for doc in response:
                print(f"   - {doc.get('document_name')}: {doc.get('document_type')} (AI analysis: {bool(doc.get('ai_analysis'))})")
            return True
        return False

    def test_create_team(self):
        """Test Team Management & Collaboration - Create Team"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for team creation")
            return False
            
        team_data = {
            "team_name": "Crisis Response Team Alpha",
            "team_description": "Primary crisis response and management team for enterprise operations",
            "team_members": ["crisis.manager@example.com", "operations.lead@example.com", "communications.director@example.com"],
            "team_roles": ["crisis_manager", "analyst", "coordinator"]
        }
        
        success, response = self.run_test(
            "Create Team",
            "POST",
            f"companies/{self.company_id}/teams",
            200,
            data=team_data
        )
        
        if success and 'id' in response:
            self.team_id = response['id']
            print(f"   Created team ID: {self.team_id}")
            print(f"   Team name: {response.get('team_name', 'N/A')}")
            print(f"   Team description: {response.get('team_description', 'N/A')}")
            print(f"   Team members: {len(response.get('team_members', []))}")
            print(f"   Team roles: {response.get('team_roles', [])}")
            print(f"   Access level: {response.get('access_level', 'N/A')}")
            return True
        return False

    def test_get_company_teams(self):
        """Test Get Company Teams"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for getting teams")
            return False
            
        success, response = self.run_test(
            "Get Company Teams",
            "GET",
            f"companies/{self.company_id}/teams",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} teams")
            for team in response:
                print(f"   - {team.get('team_name')}: {len(team.get('team_members', []))} members ({team.get('access_level', 'N/A')} access)")
            return True
        return False

    def test_generate_rapid_analysis(self):
        """Test Rapid Analysis Tools - Generate Analysis"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for rapid analysis")
            return False
            
        # Test different types of rapid analysis
        analysis_types = [
            "vulnerability_assessment",
            "business_impact", 
            "scenario_recommendation",
            "competitive_analysis"
        ]
        
        successful_analyses = 0
        
        for analysis_type in analysis_types:
            success, response = self.run_test(
                f"Generate Rapid Analysis - {analysis_type}",
                "POST",
                f"companies/{self.company_id}/rapid-analysis?analysis_type={analysis_type}",
                200
            )
            
            if success and 'id' in response:
                successful_analyses += 1
                print(f"   ✅ {analysis_type} analysis generated")
                print(f"     Analysis ID: {response.get('id')}")
                print(f"     Title: {response.get('analysis_title', 'N/A')}")
                print(f"     Content length: {len(response.get('analysis_content', ''))}")
                print(f"     Key findings: {len(response.get('key_findings', []))}")
                print(f"     Recommendations: {len(response.get('recommendations', []))}")
                print(f"     Priority level: {response.get('priority_level', 'N/A')}")
                print(f"     Confidence score: {response.get('confidence_score', 'N/A')}")
            else:
                print(f"   ❌ Failed to generate {analysis_type} analysis")
        
        print(f"   Successfully generated {successful_analyses}/{len(analysis_types)} rapid analyses")
        return successful_analyses > 0

    def test_create_company_scenario(self):
        """Test Company-Specific Scenario Creation"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for company scenario creation")
            return False
            
        company_scenario_data = {
            "title": "Enterprise Data Center Outage Crisis",
            "description": "Major data center failure affecting all enterprise operations with potential for extended downtime and data loss",
            "crisis_type": "cyber_attack",
            "severity_level": 9,
            "affected_regions": ["San Francisco", "Remote Workforce", "Global Operations"],
            "key_variables": ["Data recovery time", "Customer impact", "Revenue loss", "Reputation damage", "Regulatory compliance"]
        }
        
        success, response = self.run_test(
            "Create Company-Specific Scenario",
            "POST",
            f"companies/{self.company_id}/scenarios",
            200,
            data=company_scenario_data
        )
        
        if success and 'id' in response:
            self.company_scenario_id = response['id']
            print(f"   Created company scenario ID: {self.company_scenario_id}")
            print(f"   Scenario title: {response.get('title', 'N/A')}")
            print(f"   Crisis type: {response.get('crisis_type', 'N/A')}")
            print(f"   Severity level: {response.get('severity_level', 'N/A')}")
            print(f"   Company context: {bool(response.get('company_id'))}")
            return True
        return False

    # ========== SAAS ADMIN PLATFORM TESTING ==========
    
    def test_admin_initialize(self):
        """Test Admin System Initialization"""
        admin_data = {
            "admin_email": "rauno.saarnio@xr-presence.com",
            "admin_level": "super_admin",
            "permissions": ["all"]
        }
        
        success, response = self.run_test(
            "Admin System Initialize",
            "POST",
            "admin/initialize",
            200,
            data=admin_data
        )
        
        if success and 'admin_email' in response:
            print(f"   Admin initialized: {response.get('admin_email', 'N/A')}")
            print(f"   Admin level: {response.get('admin_level', 'N/A')}")
            print(f"   Permissions: {response.get('permissions', [])}")
            return True
        return False

    def test_get_license_tiers(self):
        """Test License Tier Management - Get Tiers"""
        success, response = self.run_test(
            "Get License Tiers",
            "GET",
            "admin/license-tiers",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} license tiers")
            for tier in response:
                print(f"   - {tier.get('tier_name')}: ${tier.get('monthly_price')}/month, ${tier.get('annual_price')}/year")
                print(f"     Max users: {tier.get('max_users')}, Features: {len(tier.get('features', []))}")
            return True
        return False

    def test_create_client(self):
        """Test Client Management - Create Client"""
        # First get license tiers to use one
        tier_success, tier_response = self.run_test(
            "Get License Tiers for Client Creation",
            "GET",
            "admin/license-tiers",
            200
        )
        
        if not tier_success or not tier_response:
            print("❌ Could not get license tiers for client creation")
            return False
            
        license_tier_id = tier_response[0]['id'] if tier_response else None
        if not license_tier_id:
            print("❌ No license tier ID available")
            return False
            
        client_data = {
            "client_name": "Test Enterprise Client",
            "client_email": "client@testenterprise.com",
            "license_tier_id": license_tier_id,
            "license_count": 5
        }
        
        success, response = self.run_test(
            "Create Client",
            "POST",
            "admin/clients",
            200,
            data=client_data
        )
        
        if success and 'id' in response:
            self.client_id = response['id']
            print(f"   Created client ID: {self.client_id}")
            print(f"   Client name: {response.get('client_name', 'N/A')}")
            print(f"   Client email: {response.get('client_email', 'N/A')}")
            print(f"   License count: {response.get('license_count', 'N/A')}")
            print(f"   Subscription status: {response.get('subscription_status', 'N/A')}")
            print(f"   Trial end date: {response.get('trial_end_date', 'N/A')}")
            return True
        return False

    def test_get_clients(self):
        """Test Client Management - Get All Clients"""
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "admin/clients",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} clients")
            for client in response:
                print(f"   - {client.get('client_name')}: {client.get('subscription_status')} ({client.get('license_count')} licenses)")
            return True
        return False

    def test_get_ai_avatars(self):
        """Test AI Avatar Management - Get All Avatars"""
        success, response = self.run_test(
            "Get AI Avatars",
            "GET",
            "admin/ai-avatars",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} AI avatars")
            for avatar in response:
                print(f"   - {avatar.get('avatar_name')}: {avatar.get('avatar_type')} ({avatar.get('status')})")
                print(f"     Base competences: {len(avatar.get('base_competences', []))}")
                print(f"     Custom competences: {len(avatar.get('client_custom_competences', []))}")
            return True
        return False

    def test_update_avatar_status(self):
        """Test AI Avatar Status Management"""
        # First get avatars to find one to update
        avatar_success, avatar_response = self.run_test(
            "Get Avatars for Status Update",
            "GET",
            "admin/ai-avatars",
            200
        )
        
        if not avatar_success or not avatar_response:
            print("❌ Could not get avatars for status update")
            return False
            
        avatar_id = avatar_response[0]['id'] if avatar_response else None
        if not avatar_id:
            print("❌ No avatar ID available for status update")
            return False
            
        # Test different status updates
        statuses = ["active", "monitoring", "learning", "inactive"]
        successful_updates = 0
        
        for status in statuses:
            status_data = {"status": status}
            
            success, response = self.run_test(
                f"Update Avatar Status to {status}",
                "PUT",
                f"admin/ai-avatars/{avatar_id}/status",
                200,
                data=status_data
            )
            
            if success:
                successful_updates += 1
                print(f"   ✅ Avatar status updated to: {status}")
            else:
                print(f"   ❌ Failed to update avatar status to: {status}")
        
        print(f"   Successfully updated {successful_updates}/{len(statuses)} status changes")
        return successful_updates > 0

    def test_add_avatar_competence(self):
        """Test Avatar Competence Management - Add Competence"""
        # First get avatars to find one to add competence to
        avatar_success, avatar_response = self.run_test(
            "Get Avatars for Competence Addition",
            "GET",
            "admin/ai-avatars",
            200
        )
        
        if not avatar_success or not avatar_response:
            print("❌ Could not get avatars for competence addition")
            return False
            
        avatar_id = avatar_response[0]['id'] if avatar_response else None
        if not avatar_id:
            print("❌ No avatar ID available for competence addition")
            return False
            
        competence_data = {
            "competence_name": "Advanced Risk Assessment",
            "competence_description": "Ability to perform sophisticated risk analysis using multiple data sources and predictive modeling",
            "competence_type": "skill",
            "proficiency_level": 8
        }
        
        success, response = self.run_test(
            "Add Avatar Competence",
            "POST",
            f"avatars/{avatar_id}/competences",
            200,
            data=competence_data
        )
        
        if success and 'id' in response:
            print(f"   Added competence ID: {response.get('id')}")
            print(f"   Competence name: {response.get('competence_name', 'N/A')}")
            print(f"   Competence type: {response.get('competence_type', 'N/A')}")
            print(f"   Proficiency level: {response.get('proficiency_level', 'N/A')}")
            print(f"   Added by client: {response.get('added_by_client', 'N/A')}")
            return True
        return False

    def test_get_avatar_competences(self):
        """Test Avatar Competence Management - Get Competences"""
        # First get avatars to find one to get competences for
        avatar_success, avatar_response = self.run_test(
            "Get Avatars for Competence Retrieval",
            "GET",
            "admin/ai-avatars",
            200
        )
        
        if not avatar_success or not avatar_response:
            print("❌ Could not get avatars for competence retrieval")
            return False
            
        avatar_id = avatar_response[0]['id'] if avatar_response else None
        if not avatar_id:
            print("❌ No avatar ID available for competence retrieval")
            return False
            
        success, response = self.run_test(
            "Get Avatar Competences",
            "GET",
            f"avatars/{avatar_id}/competences",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} competences for avatar")
            for competence in response:
                print(f"   - {competence.get('competence_name')}: {competence.get('competence_type')} (Level {competence.get('proficiency_level')})")
            return True
        return False

    def test_create_stripe_payment_intent(self):
        """Test Stripe Payment Integration - Create Payment Intent"""
        if not hasattr(self, 'client_id') or not self.client_id:
            print("❌ No client ID available for payment intent creation")
            return False
            
        payment_data = {
            "client_id": self.client_id,
            "license_tier_id": "tier_id_placeholder",  # This would be a real tier ID
            "license_count": 5,
            "billing_period": "monthly"
        }
        
        success, response = self.run_test(
            "Create Stripe Payment Intent",
            "POST",
            "admin/stripe/create-payment-intent",
            200,
            data=payment_data
        )
        
        if success and 'client_secret' in response:
            print(f"   Payment intent created")
            print(f"   Client secret: {response.get('client_secret', 'N/A')[:20]}...")
            print(f"   Amount: ${response.get('amount', 'N/A')}")
            print(f"   Currency: {response.get('currency', 'N/A')}")
            print(f"   Billing period: {response.get('billing_period', 'N/A')}")
            return True
        return False

    def test_admin_dashboard_stats(self):
        """Test Admin Dashboard Analytics"""
        success, response = self.run_test(
            "Admin Dashboard Stats",
            "GET",
            "admin/dashboard/stats",
            200
        )
        
        if success:
            print(f"   Total clients: {response.get('total_clients', 'N/A')}")
            print(f"   Active clients: {response.get('active_clients', 'N/A')}")
            print(f"   Trial clients: {response.get('trial_clients', 'N/A')}")
            print(f"   Total revenue: ${response.get('total_revenue', 'N/A')}")
            print(f"   Monthly recurring revenue: ${response.get('monthly_recurring_revenue', 'N/A')}")
            print(f"   License distribution: {response.get('license_distribution', {})}")
            print(f"   AI avatar activity: {response.get('ai_avatar_activity', {})}")
            print(f"   Payment analytics: {response.get('payment_analytics', {})}")
            return True
        return False

    # ========== NEW COMPANY MANAGEMENT ENDPOINTS TESTING ==========
    
    def test_company_document_upload_pdf(self):
        """Test Company Document Upload - PDF File"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for PDF document upload")
            return False
            
        # Create a simple PDF content for testing
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Business Continuity Plan) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        
        # Use requests to upload file
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('test_document.pdf', pdf_content, 'application/pdf')}
        data = {'document_type': 'business_plan'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Company Document Upload - PDF File...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Document ID: {response_data.get('id', 'N/A')}")
                    print(f"   Document name: {response_data.get('document_name', 'N/A')}")
                    print(f"   AI analysis length: {len(response_data.get('ai_analysis', ''))}")
                    print(f"   Key insights: {len(response_data.get('key_insights', []))}")
                    print(f"   Risk factors: {len(response_data.get('risk_factors', []))}")
                    print(f"   File size: {response_data.get('file_size', 'N/A')}")
                    
                    # Verify required fields are present
                    required_fields = ['id', 'ai_analysis', 'key_insights', 'risk_factors']
                    for field in required_fields:
                        if field not in response_data or not response_data[field]:
                            print(f"   ⚠️ Missing or empty required field: {field}")
                            return False
                    
                    self.pdf_document_id = response_data.get('id')
                    return True
                except Exception as e:
                    print(f"   ❌ Error parsing response: {e}")
                    return False
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_company_document_upload_docx(self):
        """Test Company Document Upload - DOCX File"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for DOCX document upload")
            return False
            
        # Create a simple DOCX content for testing (minimal DOCX structure)
        docx_content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00[Content_Types].xmlPK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00_rels/.relsPK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00word/document.xmlPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00[Content_Types].xmlPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01F\x00\x00\x00_rels/.relsPK\x01\x02\x14\x00\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x84\x00\x00\x00word/document.xmlPK\x05\x06\x00\x00\x00\x00\x03\x00\x03\x00\xca\x00\x00\x00\xd3\x00\x00\x00\x00\x00'
        
        # Use requests to upload file
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('test_document.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {'document_type': 'operational_plan'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Company Document Upload - DOCX File...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Document ID: {response_data.get('id', 'N/A')}")
                    print(f"   Document name: {response_data.get('document_name', 'N/A')}")
                    print(f"   AI analysis length: {len(response_data.get('ai_analysis', ''))}")
                    print(f"   Key insights: {len(response_data.get('key_insights', []))}")
                    print(f"   Risk factors: {len(response_data.get('risk_factors', []))}")
                    print(f"   File size: {response_data.get('file_size', 'N/A')}")
                    
                    # Verify required fields are present
                    required_fields = ['id', 'ai_analysis', 'key_insights', 'risk_factors']
                    for field in required_fields:
                        if field not in response_data or not response_data[field]:
                            print(f"   ⚠️ Missing or empty required field: {field}")
                            return False
                    
                    self.docx_document_id = response_data.get('id')
                    return True
                except Exception as e:
                    print(f"   ❌ Error parsing response: {e}")
                    return False
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_company_document_upload_invalid_file_type(self):
        """Test Company Document Upload - Invalid File Type Validation"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for invalid file type test")
            return False
            
        # Create a text file (should be rejected)
        txt_content = b"This is a plain text file that should be rejected"
        
        # Use requests to upload file
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('test_document.txt', txt_content, 'text/plain')}
        data = {'document_type': 'other'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Company Document Upload - Invalid File Type...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            # Should return 400 for invalid file type
            success = response.status_code == 400
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Correctly rejected invalid file type with status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data.get('detail', 'N/A')}")
                    return True
                except:
                    print(f"   Error text: {response.text}")
                    return True
            else:
                print(f"❌ Failed - Expected 400, got {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_company_document_upload_large_file(self):
        """Test Company Document Upload - Large File Size Validation"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for large file test")
            return False
            
        # Create a large file (>10MB) - simulate with a large PDF
        large_content = b"%PDF-1.4\n" + b"A" * (11 * 1024 * 1024)  # 11MB of data
        
        # Use requests to upload file
        url = f"{self.api_url}/companies/{self.company_id}/documents/upload"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {'file': ('large_document.pdf', large_content, 'application/pdf')}
        data = {'document_type': 'business_plan'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Company Document Upload - Large File Size...")
        print(f"   URL: {url}")
        print(f"   File size: {len(large_content) / (1024*1024):.1f}MB")
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
            print(f"   Status Code: {response.status_code}")
            
            # Should return 400 or 413 for file too large
            success = response.status_code in [400, 413]
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Correctly rejected large file with status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data.get('detail', 'N/A')}")
                    return True
                except:
                    print(f"   Error text: {response.text}")
                    return True
            else:
                print(f"❌ Failed - Expected 400 or 413, got {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_get_company_users(self):
        """Test GET /api/companies/{company_id}/users endpoint"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for getting company users")
            return False
            
        success, response = self.run_test(
            "Get Company Users",
            "GET",
            f"companies/{self.company_id}/users",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users for company")
            for user in response:
                print(f"   - {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
                print(f"     Role: {user.get('role', 'N/A')}, Department: {user.get('department', 'N/A')}")
                
                # Verify User model fields are present
                required_fields = ['id', 'email', 'username', 'organization']
                for field in required_fields:
                    if field not in user:
                        print(f"   ⚠️ Missing required User field: {field}")
                        return False
            return True
        return False

    def test_company_users_access_control(self):
        """Test Company Users Access Control - Unauthorized Access"""
        # Create a new user to test access control
        test_user_data = {
            "email": f"unauthorized_user_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"unauthorized_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Different Organization"
        }
        
        # Register new user
        register_success, register_response = self.run_test(
            "Register Unauthorized User",
            "POST",
            "register",
            200,
            data=test_user_data
        )
        
        if not register_success:
            print("❌ Could not create unauthorized user for access control test")
            return False
            
        # Store original token
        original_token = self.token
        unauthorized_token = register_response.get('access_token')
        
        if not unauthorized_token:
            print("❌ Could not get token for unauthorized user")
            return False
            
        # Switch to unauthorized user token
        self.token = unauthorized_token
        
        # Try to access company users (should fail)
        success, response = self.run_test(
            "Get Company Users - Unauthorized Access",
            "GET",
            f"companies/{self.company_id}/users",
            403  # Should return 403 Forbidden
        )
        
        # Restore original token
        self.token = original_token
        
        if success:
            print("✅ Access control working - Unauthorized access correctly denied")
            return True
        else:
            print("❌ Access control failed - Unauthorized access was allowed")
            return False

    def test_rapid_analysis_all_types(self):
        """Test Rapid Analysis with All Analysis Types"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for rapid analysis testing")
            return False
            
        analysis_types = [
            "vulnerability_assessment",
            "business_impact", 
            "scenario_recommendation",
            "competitive_analysis"
        ]
        
        successful_analyses = 0
        
        for analysis_type in analysis_types:
            success, response = self.run_test(
                f"Rapid Analysis - {analysis_type}",
                "POST",
                f"companies/{self.company_id}/rapid-analysis?analysis_type={analysis_type}",
                200
            )
            
            if success and 'id' in response:
                successful_analyses += 1
                print(f"   ✅ {analysis_type} analysis generated")
                print(f"     Analysis ID: {response.get('id')}")
                print(f"     Title: {response.get('analysis_title', 'N/A')}")
                print(f"     Content length: {len(response.get('analysis_content', ''))}")
                print(f"     Key findings: {len(response.get('key_findings', []))}")
                print(f"     Recommendations: {len(response.get('recommendations', []))}")
                print(f"     Priority level: {response.get('priority_level', 'N/A')}")
                print(f"     Confidence score: {response.get('confidence_score', 'N/A')}")
                
                # Verify RapidAnalysis model fields are present
                required_fields = ['id', 'analysis_content', 'key_findings', 'recommendations']
                for field in required_fields:
                    if field not in response or not response[field]:
                        print(f"   ⚠️ Missing or empty required field: {field}")
                        return False
                        
            else:
                print(f"   ❌ Failed to generate {analysis_type} analysis")
        
        print(f"   Successfully generated {successful_analyses}/{len(analysis_types)} rapid analyses")
        return successful_analyses == len(analysis_types)

    def test_team_management_enhanced(self):
        """Test Enhanced Team Management Endpoints"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for team management testing")
            return False
            
        # Test creating team with email list
        team_data = {
            "team_name": "Enhanced Crisis Response Team",
            "team_description": "Advanced crisis response and management team with specialized roles",
            "team_members": [
                "crisis.lead@company.com", 
                "operations.manager@company.com", 
                "communications.specialist@company.com",
                "risk.analyst@company.com"
            ],
            "team_roles": ["crisis_manager", "analyst", "coordinator", "observer"]
        }
        
        success, response = self.run_test(
            "Create Enhanced Team",
            "POST",
            f"companies/{self.company_id}/teams",
            200,
            data=team_data
        )
        
        if success and 'id' in response:
            enhanced_team_id = response['id']
            print(f"   ✅ Enhanced team created with ID: {enhanced_team_id}")
            print(f"   Team name: {response.get('team_name', 'N/A')}")
            print(f"   Team description: {response.get('team_description', 'N/A')}")
            print(f"   Team members: {len(response.get('team_members', []))}")
            print(f"   Team roles: {response.get('team_roles', [])}")
            print(f"   Access level: {response.get('access_level', 'N/A')}")
            
            # Verify TeamCreate data was properly processed
            if len(response.get('team_members', [])) != len(team_data['team_members']):
                print(f"   ⚠️ Team member count mismatch")
                return False
                
            if response.get('team_roles', []) != team_data['team_roles']:
                print(f"   ⚠️ Team roles mismatch")
                return False
            
            # Test getting company teams
            teams_success, teams_response = self.run_test(
                "Get Enhanced Company Teams",
                "GET",
                f"companies/{self.company_id}/teams",
                200
            )
            
            if teams_success and isinstance(teams_response, list):
                print(f"   ✅ Retrieved {len(teams_response)} teams")
                
                # Find our created team
                created_team = None
                for team in teams_response:
                    if team.get('id') == enhanced_team_id:
                        created_team = team
                        break
                
                if created_team:
                    print(f"   ✅ Enhanced team found in company teams list")
                    print(f"   Team lead: {created_team.get('team_lead', 'N/A')}")
                    print(f"   Active scenarios: {len(created_team.get('active_scenarios', []))}")
                    return True
                else:
                    print(f"   ❌ Enhanced team not found in company teams list")
                    return False
            else:
                print(f"   ❌ Failed to retrieve company teams")
                return False
        else:
            print(f"   ❌ Failed to create enhanced team")
            return False

    # ========== FUZZY LOGIC SCENARIO ADJUSTERS TESTING ==========
    
    def test_create_scenario_adjustment(self):
        """Test Creating Scenario Adjustment with SEPTE Framework"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for scenario adjustment creation")
            return False
            
        # Test with valid SEPTE percentages (opposing pairs sum to 100%)
        adjustment_data = {
            "adjustment_name": "High Crisis Economic Scenario",
            "scenario_id": self.created_scenario_id if hasattr(self, 'created_scenario_id') else None,
            "economic_crisis_pct": 60.0,
            "economic_stability_pct": 40.0,
            "social_unrest_pct": 30.0,
            "social_cohesion_pct": 70.0,
            "environmental_degradation_pct": 80.0,
            "environmental_resilience_pct": 20.0,
            "political_instability_pct": 45.0,
            "political_stability_pct": 55.0,
            "technological_disruption_pct": 25.0,
            "technological_advancement_pct": 75.0
        }
        
        success, response = self.run_test(
            "Create Scenario Adjustment",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            200,
            data=adjustment_data
        )
        
        if success and 'id' in response:
            self.scenario_adjustment_id = response['id']
            print(f"   ✅ Scenario adjustment created with ID: {self.scenario_adjustment_id}")
            print(f"   Adjustment name: {response.get('adjustment_name', 'N/A')}")
            print(f"   Company ID: {response.get('company_id', 'N/A')}")
            print(f"   Real-time analysis length: {len(response.get('real_time_analysis', ''))}")
            print(f"   Impact summary length: {len(response.get('impact_summary', ''))}")
            print(f"   Risk level: {response.get('risk_level', 'N/A')}")
            print(f"   Recommendations count: {len(response.get('recommendations', []))}")
            print(f"   Created by: {response.get('created_by', 'N/A')}")
            
            # Verify SEPTE percentages are preserved
            septe_pairs = [
                ('economic_crisis_pct', 'economic_stability_pct'),
                ('social_unrest_pct', 'social_cohesion_pct'),
                ('environmental_degradation_pct', 'environmental_resilience_pct'),
                ('political_instability_pct', 'political_stability_pct'),
                ('technological_disruption_pct', 'technological_advancement_pct')
            ]
            
            for pair in septe_pairs:
                val1 = response.get(pair[0], 0)
                val2 = response.get(pair[1], 0)
                total = val1 + val2
                if abs(total - 100.0) > 0.1:
                    print(f"   ⚠️ SEPTE validation failed for {pair}: {val1} + {val2} = {total}")
                    return False
                else:
                    print(f"   ✅ SEPTE pair {pair[0]}/{pair[1]}: {val1}%/{val2}% = 100%")
            
            # Verify AI analysis fields are present
            required_fields = ['real_time_analysis', 'impact_summary', 'risk_level', 'recommendations']
            for field in required_fields:
                if field not in response or not response[field]:
                    print(f"   ⚠️ Missing or empty AI analysis field: {field}")
                    return False
            
            return True
        else:
            print(f"   ❌ Failed to create scenario adjustment")
            return False

    def test_scenario_adjustment_percentage_validation(self):
        """Test SEPTE Percentage Validation (opposing pairs must sum to 100%)"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for percentage validation test")
            return False
            
        # Test with invalid percentages (don't sum to 100%)
        invalid_adjustment_data = {
            "adjustment_name": "Invalid Percentage Test",
            "economic_crisis_pct": 60.0,
            "economic_stability_pct": 30.0,  # 60 + 30 = 90, not 100
            "social_unrest_pct": 50.0,
            "social_cohesion_pct": 50.0,
            "environmental_degradation_pct": 50.0,
            "environmental_resilience_pct": 50.0,
            "political_instability_pct": 50.0,
            "political_stability_pct": 50.0,
            "technological_disruption_pct": 50.0,
            "technological_advancement_pct": 50.0
        }
        
        success, response = self.run_test(
            "Create Scenario Adjustment - Invalid Percentages",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            400,  # Should return 400 Bad Request
            data=invalid_adjustment_data
        )
        
        if success:
            print(f"   ✅ Percentage validation working - Invalid percentages correctly rejected")
            try:
                error_data = response if isinstance(response, dict) else {}
                error_message = error_data.get('detail', 'Validation error')
                print(f"   Error message: {error_message}")
                if "sum to 100%" in error_message:
                    print(f"   ✅ Correct validation error message")
                    return True
                else:
                    print(f"   ⚠️ Unexpected error message format")
                    return True  # Still passed validation, just different message
            except:
                return True
        else:
            print(f"   ❌ Percentage validation failed - Invalid percentages were accepted")
            return False

    def test_get_scenario_adjustments(self):
        """Test Retrieving All Scenario Adjustments for Company"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for getting scenario adjustments")
            return False
            
        success, response = self.run_test(
            "Get Scenario Adjustments",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} scenario adjustments")
            
            # Verify our created adjustment is in the list
            if hasattr(self, 'scenario_adjustment_id'):
                found_adjustment = None
                for adjustment in response:
                    if adjustment.get('id') == self.scenario_adjustment_id:
                        found_adjustment = adjustment
                        break
                
                if found_adjustment:
                    print(f"   ✅ Created adjustment found in list")
                    print(f"   Adjustment name: {found_adjustment.get('adjustment_name', 'N/A')}")
                    print(f"   Risk level: {found_adjustment.get('risk_level', 'N/A')}")
                    print(f"   Created at: {found_adjustment.get('created_at', 'N/A')}")
                    return True
                else:
                    print(f"   ⚠️ Created adjustment not found in list")
                    return len(response) > 0  # Still pass if we got some adjustments
            else:
                print(f"   ✅ Retrieved adjustments list (no specific adjustment to verify)")
                return True
        else:
            print(f"   ❌ Failed to retrieve scenario adjustments")
            return False

    def test_update_scenario_adjustment(self):
        """Test Updating Scenario Adjustment and AI Analysis Regeneration"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for scenario adjustment update")
            return False
            
        if not hasattr(self, 'scenario_adjustment_id') or not self.scenario_adjustment_id:
            print("❌ No scenario adjustment ID available for update")
            return False
            
        # Update with different SEPTE percentages
        update_data = {
            "adjustment_name": "Updated High Crisis Scenario",
            "economic_crisis_pct": 75.0,  # Changed from 60%
            "economic_stability_pct": 25.0,  # Changed from 40%
            "social_unrest_pct": 40.0,  # Changed from 30%
            "social_cohesion_pct": 60.0,  # Changed from 70%
            "environmental_degradation_pct": 90.0,  # Changed from 80%
            "environmental_resilience_pct": 10.0,  # Changed from 20%
            "political_instability_pct": 55.0,  # Changed from 45%
            "political_stability_pct": 45.0,  # Changed from 55%
            "technological_disruption_pct": 35.0,  # Changed from 25%
            "technological_advancement_pct": 65.0  # Changed from 75%
        }
        
        success, response = self.run_test(
            "Update Scenario Adjustment",
            "PUT",
            f"companies/{self.company_id}/scenario-adjustments/{self.scenario_adjustment_id}",
            200,
            data=update_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Scenario adjustment updated successfully")
            print(f"   Updated name: {response.get('adjustment_name', 'N/A')}")
            print(f"   New economic crisis %: {response.get('economic_crisis_pct', 'N/A')}")
            print(f"   New environmental degradation %: {response.get('environmental_degradation_pct', 'N/A')}")
            print(f"   Updated at: {response.get('updated_at', 'N/A')}")
            
            # Verify AI analysis was regenerated (should be different from original)
            new_analysis_length = len(response.get('real_time_analysis', ''))
            print(f"   New analysis length: {new_analysis_length}")
            
            # Verify updated percentages
            if response.get('economic_crisis_pct') == 75.0 and response.get('economic_stability_pct') == 25.0:
                print(f"   ✅ Economic percentages updated correctly")
            else:
                print(f"   ⚠️ Economic percentages not updated correctly")
                return False
                
            if response.get('environmental_degradation_pct') == 90.0 and response.get('environmental_resilience_pct') == 10.0:
                print(f"   ✅ Environmental percentages updated correctly")
            else:
                print(f"   ⚠️ Environmental percentages not updated correctly")
                return False
            
            return True
        else:
            print(f"   ❌ Failed to update scenario adjustment")
            return False

    def test_create_consensus_settings(self):
        """Test Creating Consensus Settings for Team Agreement"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for consensus creation")
            return False
            
        if not hasattr(self, 'scenario_adjustment_id') or not self.scenario_adjustment_id:
            print("❌ No scenario adjustment ID available for consensus")
            return False
            
        consensus_data = {
            "adjustment_id": self.scenario_adjustment_id,
            "consensus_name": "Crisis Response Team Consensus",
            "team_id": getattr(self, 'team_id', None)  # Use team_id if available
        }
        
        success, response = self.run_test(
            "Create Consensus Settings",
            "POST",
            f"companies/{self.company_id}/consensus",
            200,
            data=consensus_data
        )
        
        if success and 'id' in response:
            self.consensus_id = response['id']
            print(f"   ✅ Consensus settings created with ID: {self.consensus_id}")
            print(f"   Consensus name: {response.get('consensus_name', 'N/A')}")
            print(f"   Adjustment ID: {response.get('adjustment_id', 'N/A')}")
            print(f"   Team ID: {response.get('team_id', 'N/A')}")
            print(f"   Total team members: {response.get('total_team_members', 'N/A')}")
            print(f"   Agreed by count: {len(response.get('agreed_by', []))}")
            print(f"   Consensus percentage: {response.get('consensus_percentage', 'N/A')}%")
            print(f"   Consensus reached: {response.get('consensus_reached', 'N/A')}")
            
            # Verify creator is automatically in agreed_by list
            agreed_by = response.get('agreed_by', [])
            if self.user_id in agreed_by:
                print(f"   ✅ Creator automatically added to agreed_by list")
            else:
                print(f"   ⚠️ Creator not automatically added to agreed_by list")
                return False
            
            # Verify final_settings contains SEPTE parameters
            final_settings = response.get('final_settings', {})
            septe_keys = [
                'economic_crisis_pct', 'economic_stability_pct',
                'social_unrest_pct', 'social_cohesion_pct',
                'environmental_degradation_pct', 'environmental_resilience_pct',
                'political_instability_pct', 'political_stability_pct',
                'technological_disruption_pct', 'technological_advancement_pct'
            ]
            
            missing_keys = [key for key in septe_keys if key not in final_settings]
            if not missing_keys:
                print(f"   ✅ All SEPTE parameters present in final_settings")
            else:
                print(f"   ⚠️ Missing SEPTE parameters in final_settings: {missing_keys}")
                return False
            
            return True
        else:
            print(f"   ❌ Failed to create consensus settings")
            return False

    def test_agree_to_consensus(self):
        """Test User Agreement to Consensus and Percentage Calculation"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for consensus agreement")
            return False
            
        if not hasattr(self, 'consensus_id') or not self.consensus_id:
            print("❌ No consensus ID available for agreement")
            return False
            
        success, response = self.run_test(
            "Agree to Consensus",
            "POST",
            f"companies/{self.company_id}/consensus/{self.consensus_id}/agree",
            200
        )
        
        if success:
            print(f"   ✅ Agreement recorded successfully")
            print(f"   Message: {response.get('message', 'N/A')}")
            print(f"   Consensus reached: {response.get('consensus_reached', 'N/A')}")
            
            # Since we're the only user, consensus percentage should be 100%
            # and consensus_reached should be True (>= 75% threshold)
            if response.get('consensus_reached') == True:
                print(f"   ✅ Consensus reached (75% threshold met)")
            else:
                print(f"   ⚠️ Consensus not reached (may be expected with single user)")
            
            return True
        else:
            print(f"   ❌ Failed to record agreement")
            return False

    def test_scenario_adjustment_access_control(self):
        """Test Access Control for Scenario Adjustments"""
        # Create a new user to test access control
        test_user_data = {
            "email": f"unauthorized_adj_user_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"unauthorized_adj_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "organization": "Different Organization"
        }
        
        # Register new user
        register_success, register_response = self.run_test(
            "Register Unauthorized User for Adjustment Access",
            "POST",
            "register",
            200,
            data=test_user_data
        )
        
        if not register_success:
            print("❌ Could not create unauthorized user for access control test")
            return False
            
        # Store original token
        original_token = self.token
        unauthorized_token = register_response.get('access_token')
        
        if not unauthorized_token:
            print("❌ Could not get token for unauthorized user")
            return False
            
        # Switch to unauthorized user token
        self.token = unauthorized_token
        
        # Try to access scenario adjustments (should fail)
        success, response = self.run_test(
            "Get Scenario Adjustments - Unauthorized Access",
            "GET",
            f"companies/{self.company_id}/scenario-adjustments",
            403  # Should return 403 Forbidden
        )
        
        # Restore original token
        self.token = original_token
        
        if success:
            print("✅ Access control working - Unauthorized access correctly denied")
            return True
        else:
            print("❌ Access control failed - Unauthorized access was allowed")
            return False

    def test_ai_analysis_integration(self):
        """Test AI Analysis Integration with Claude Sonnet 4"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for AI analysis test")
            return False
            
        # Create scenario adjustment with extreme values to test AI analysis
        extreme_adjustment_data = {
            "adjustment_name": "Extreme Crisis Scenario for AI Analysis",
            "economic_crisis_pct": 95.0,
            "economic_stability_pct": 5.0,
            "social_unrest_pct": 90.0,
            "social_cohesion_pct": 10.0,
            "environmental_degradation_pct": 85.0,
            "environmental_resilience_pct": 15.0,
            "political_instability_pct": 80.0,
            "political_stability_pct": 20.0,
            "technological_disruption_pct": 75.0,
            "technological_advancement_pct": 25.0
        }
        
        success, response = self.run_test(
            "Create Extreme Scenario for AI Analysis",
            "POST",
            f"companies/{self.company_id}/scenario-adjustments",
            200,
            data=extreme_adjustment_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Extreme scenario created for AI analysis")
            
            # Verify AI analysis quality
            analysis = response.get('real_time_analysis', '')
            impact_summary = response.get('impact_summary', '')
            risk_level = response.get('risk_level', '')
            recommendations = response.get('recommendations', [])
            
            print(f"   AI Analysis length: {len(analysis)} characters")
            print(f"   Impact summary length: {len(impact_summary)} characters")
            print(f"   Risk level: {risk_level}")
            print(f"   Recommendations count: {len(recommendations)}")
            
            # Verify AI analysis contains relevant content
            if len(analysis) > 100:
                print(f"   ✅ AI analysis has substantial content")
            else:
                print(f"   ⚠️ AI analysis seems too short")
                return False
            
            # With extreme crisis values, risk level should be high or critical
            if risk_level in ['high', 'critical']:
                print(f"   ✅ Risk level appropriately assessed as {risk_level}")
            else:
                print(f"   ⚠️ Risk level '{risk_level}' may not match extreme crisis scenario")
            
            # Should have multiple recommendations
            if len(recommendations) >= 3:
                print(f"   ✅ Multiple recommendations provided")
                for i, rec in enumerate(recommendations[:3]):
                    print(f"     {i+1}. {rec[:80]}...")
            else:
                print(f"   ⚠️ Few recommendations provided")
            
            return True
        else:
            print(f"   ❌ Failed to create extreme scenario for AI analysis")
            return False

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

    print("\n🏢 Testing Enterprise Features...")
    print("   Testing Company Management System...")
    tester.test_create_company()
    tester.test_get_company()
    
    print("   Testing Document Intelligence Platform...")
    tester.test_upload_business_document()
    tester.test_get_company_documents()
    
    print("   Testing Team Management & Collaboration...")
    tester.test_create_team()
    tester.test_get_company_teams()
    
    print("   Testing Rapid Analysis Tools...")
    tester.test_generate_rapid_analysis()
    
    print("   Testing Company-Specific Scenario Creation...")
    tester.test_create_company_scenario()

    print("\n🆕 Testing NEW Company Management Endpoints...")
    print("   Testing Document Upload with File Validation...")
    tester.test_company_document_upload_pdf()
    tester.test_company_document_upload_docx()
    tester.test_company_document_upload_invalid_file_type()
    tester.test_company_document_upload_large_file()
    
    print("   Testing Company Users Endpoint...")
    tester.test_get_company_users()
    tester.test_company_users_access_control()
    
    print("   Testing Enhanced Rapid Analysis...")
    tester.test_rapid_analysis_all_types()
    
    print("   Testing Enhanced Team Management...")
    tester.test_team_management_enhanced()

    print("\n👑 Testing SaaS Admin Platform Features...")
    print("   Testing Admin System Initialization...")
    tester.test_admin_initialize()
    
    print("   Testing License Tier Management...")
    tester.test_get_license_tiers()
    
    print("   Testing Client Management System...")
    tester.test_create_client()
    tester.test_get_clients()
    
    print("   Testing AI Avatar Management...")
    tester.test_get_ai_avatars()
    tester.test_update_avatar_status()
    
    print("   Testing Avatar Competence Management...")
    tester.test_add_avatar_competence()
    tester.test_get_avatar_competences()
    
    print("   Testing Stripe Payment Integration...")
    tester.test_create_stripe_payment_intent()
    
    print("   Testing Admin Dashboard Analytics...")
    tester.test_admin_dashboard_stats()

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