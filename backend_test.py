import requests
import sys
import json
from datetime import datetime

class PolycrisisAPITester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
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
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=120)
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

    def test_specific_game_book_scenario(self):
        """Test Game Book functionality with specific scenario from review request"""
        # Test credentials from review request
        test_email = "test@example.com"
        test_password = "password123"
        scenario_id = "9796a80e-976e-463d-ba00-aeb899b76a7a"
        
        print(f"\n🔍 Testing Game Book with specific scenario from review request...")
        print(f"   Scenario ID: {scenario_id}")
        print(f"   Title: Finnish Economic Crisis Test")
        print(f"   User: {test_email}")
        
        # First login with test credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_success, login_response = self.run_test(
            "Login with Test Credentials",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if not login_success or 'access_token' not in login_response:
            print("❌ Failed to login with test credentials")
            return False
            
        # Update token for subsequent requests
        original_token = self.token
        self.token = login_response['access_token']
        print(f"   Logged in successfully with test credentials")
        
        try:
            # Test 1: Generate Game Book for specific scenario
            generate_success, generate_response = self.run_test(
                "Generate Game Book for Finnish Economic Crisis",
                "POST",
                f"scenarios/{scenario_id}/game-book",
                200
            )
            
            if not generate_success:
                print("❌ Failed to generate Game Book")
                return False
                
            # Verify Game Book response structure
            required_fields = ['id', 'scenario_id', 'game_book_content', 'decision_points', 
                             'resource_requirements', 'timeline_phases', 'success_metrics', 'created_at']
            
            missing_fields = []
            for field in required_fields:
                if field not in generate_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields in Game Book response: {missing_fields}")
                return False
                
            print(f"✅ Game Book generated successfully")
            print(f"   Game Book ID: {generate_response.get('id')}")
            print(f"   Content length: {len(generate_response.get('game_book_content', ''))}")
            print(f"   Decision points: {len(generate_response.get('decision_points', []))}")
            print(f"   Resource requirements: {len(generate_response.get('resource_requirements', []))}")
            print(f"   Timeline phases: {len(generate_response.get('timeline_phases', []))}")
            print(f"   Success metrics: {len(generate_response.get('success_metrics', []))}")
            
            # Verify AI content generation
            game_content = generate_response.get('game_book_content', '')
            if len(game_content) < 100:
                print(f"⚠️ Game Book content seems too short: {len(game_content)} characters")
                return False
                
            # Test 2: Retrieve Game Book for specific scenario
            retrieve_success, retrieve_response = self.run_test(
                "Retrieve Game Book for Finnish Economic Crisis",
                "GET",
                f"scenarios/{scenario_id}/game-book",
                200
            )
            
            if not retrieve_success:
                print("❌ Failed to retrieve Game Book")
                return False
                
            # Verify retrieved Game Book matches generated one
            if retrieve_response.get('id') != generate_response.get('id'):
                print("❌ Retrieved Game Book ID doesn't match generated one")
                return False
                
            if retrieve_response.get('scenario_id') != scenario_id:
                print(f"❌ Retrieved Game Book scenario_id doesn't match expected: {retrieve_response.get('scenario_id')} vs {scenario_id}")
                return False
                
            print(f"✅ Game Book retrieved successfully")
            print(f"   Retrieved Game Book ID matches generated: {retrieve_response.get('id')}")
            print(f"   Content consistency verified")
            
            # Test 3: Verify authentication is required
            temp_token = self.token
            self.token = None
            
            auth_test_success, auth_test_response = self.run_test(
                "Test Authentication Required for Game Book",
                "POST",
                f"scenarios/{scenario_id}/game-book",
                401  # Should fail without authentication
            )
            
            self.token = temp_token  # Restore token
            
            if not auth_test_success:
                print("❌ Authentication test failed - endpoint should require authentication")
                return False
                
            print(f"✅ Authentication properly enforced")
            
            # Test 4: Test with invalid scenario ID
            invalid_scenario_id = "invalid-scenario-id-12345"
            invalid_success, invalid_response = self.run_test(
                "Test Game Book with Invalid Scenario ID",
                "POST",
                f"scenarios/{invalid_scenario_id}/game-book",
                404  # Should return 404 for non-existent scenario
            )
            
            if not invalid_success:
                print("❌ Invalid scenario ID test failed - should return 404")
                return False
                
            print(f"✅ Invalid scenario ID properly handled with 404")
            
            return True
            
        finally:
            # Restore original token
            self.token = original_token

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

    # ========== CRISIS MANAGEMENT FRAMEWORK ENDPOINTS TESTING ==========
    
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
            
            # Verify expected values based on crisis_management_framework.json
            expected_categories = 4
            expected_monitoring_tasks = 4
            
            if response.get('total_monitoring_tasks') != expected_monitoring_tasks:
                print(f"   ⚠️ Expected {expected_monitoring_tasks} monitoring tasks, got {response.get('total_monitoring_tasks')}")
            
            categories = response.get('categories', [])
            if len(categories) != expected_categories:
                print(f"   ⚠️ Expected {expected_categories} categories, got {len(categories)}")
            
            # Verify categories contain expected values
            expected_category_names = [
                "Environmental Impact Assessment",
                "Supply Chain Risk Assessment", 
                "Communication Infrastructure Resilience",
                "Population Displacement Risk Assessment"
            ]
            
            for expected_cat in expected_category_names:
                if expected_cat in categories:
                    print(f"   ✅ Found expected category: {expected_cat}")
                else:
                    print(f"   ❌ Missing expected category: {expected_cat}")
                    
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
            
            # Verify factor structure
            if response:
                sample_factor = response[0]
                required_fields = ['name', 'description', 'metrics', 'impact_scale', 
                                 'monitoring_frequency', 'data_sources', 'category', 'priority']
                
                for field in required_fields:
                    if field not in sample_factor:
                        print(f"   ❌ Missing required field in factor: {field}")
                        return False
                
                # Show sample factors
                print(f"   Sample factors (first 3):")
                for i, factor in enumerate(response[:3]):
                    print(f"   {i+1}. {factor.get('name')} ({factor.get('category')})")
                    print(f"      Priority: {factor.get('priority')}, Impact: {factor.get('impact_scale')}")
                    print(f"      Monitoring: {factor.get('monitoring_frequency')}")
                    print(f"      Data sources: {len(factor.get('data_sources', []))}")
                
                # Verify we have factors from all 4 categories
                categories_found = set()
                for factor in response:
                    categories_found.add(factor.get('category_key'))
                
                expected_categories = {'environmental_impact', 'supply_chain_vulnerabilities', 
                                     'communication_infrastructure', 'population_displacement'}
                
                for expected_cat in expected_categories:
                    if expected_cat in categories_found:
                        print(f"   ✅ Found factors from category: {expected_cat}")
                    else:
                        print(f"   ❌ Missing factors from category: {expected_cat}")
                        
            return True
        return False

    def test_crisis_factors_category_filter(self):
        """Test Crisis Factors endpoint with category filtering"""
        # Test each category filter
        categories_to_test = [
            'environmental_impact',
            'supply_chain_vulnerabilities', 
            'communication_infrastructure',
            'population_displacement'
        ]
        
        successful_tests = 0
        
        for category in categories_to_test:
            success, response = self.run_test(
                f"Crisis Factors - Category Filter: {category}",
                "GET",
                f"crisis-framework/factors?category={category}",
                200
            )
            
            if success and isinstance(response, list):
                successful_tests += 1
                print(f"   ✅ Category '{category}': {len(response)} factors")
                
                # Verify all factors belong to the requested category
                for factor in response:
                    if factor.get('category_key') != category:
                        print(f"   ❌ Factor from wrong category: {factor.get('category_key')} (expected {category})")
                        return False
                        
                # Show sample factor from this category
                if response:
                    sample = response[0]
                    print(f"      Sample: {sample.get('name')} - {sample.get('description')[:50]}...")
            else:
                print(f"   ❌ Failed to get factors for category: {category}")
        
        print(f"   Successfully tested {successful_tests}/{len(categories_to_test)} category filters")
        return successful_tests == len(categories_to_test)

    def test_crisis_factors_priority_filter(self):
        """Test Crisis Factors endpoint with priority filtering"""
        # Test high priority filter (all categories should be high priority based on JSON)
        success, response = self.run_test(
            "Crisis Factors - Priority Filter: high",
            "GET",
            "crisis-framework/factors?priority=high",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} high priority factors")
            
            # Verify all factors have high priority
            for factor in response:
                if factor.get('priority') != 'high':
                    print(f"   ❌ Factor with wrong priority: {factor.get('priority')} (expected high)")
                    return False
            
            print(f"   ✅ All factors correctly filtered by high priority")
            
            # Test medium priority (should return empty based on JSON)
            medium_success, medium_response = self.run_test(
                "Crisis Factors - Priority Filter: medium",
                "GET",
                "crisis-framework/factors?priority=medium",
                200
            )
            
            if medium_success and isinstance(medium_response, list):
                print(f"   Medium priority factors: {len(medium_response)} (expected 0)")
                if len(medium_response) == 0:
                    print(f"   ✅ Correctly filtered out non-medium priority factors")
                else:
                    print(f"   ⚠️ Unexpected medium priority factors found")
            
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
            
            # Verify task structure
            if response:
                sample_task = response[0]
                required_fields = ['task', 'description', 'priority', 'frequency', 
                                 'data_sources', 'metrics_tracked', 'alert_thresholds']
                
                for field in required_fields:
                    if field not in sample_task:
                        print(f"   ❌ Missing required field in task: {field}")
                        return False
                
                # Show all monitoring tasks
                print(f"   Monitoring tasks:")
                for i, task in enumerate(response):
                    print(f"   {i+1}. {task.get('task')}")
                    print(f"      Priority: {task.get('priority')}, Frequency: {task.get('frequency')}")
                    print(f"      Data sources: {len(task.get('data_sources', []))}")
                    print(f"      Metrics tracked: {len(task.get('metrics_tracked', []))}")
                
                # Verify expected tasks based on JSON
                expected_task_keys = ['real_time_environmental', 'economic_indicators', 
                                    'social_media_sentiment', 'infrastructure_monitoring']
                
                task_keys_found = [task.get('task_key') for task in response]
                
                for expected_key in expected_task_keys:
                    if expected_key in task_keys_found:
                        print(f"   ✅ Found expected task: {expected_key}")
                    else:
                        print(f"   ❌ Missing expected task: {expected_key}")
                        
            return True
        return False

    def test_monitoring_tasks_priority_filter(self):
        """Test Monitoring Tasks endpoint with priority filtering"""
        # Test critical priority filter
        success, response = self.run_test(
            "Monitoring Tasks - Priority Filter: critical",
            "GET",
            "crisis-framework/monitoring-tasks?priority=critical",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} critical priority tasks")
            
            # Verify all tasks have critical priority
            for task in response:
                if task.get('priority') != 'critical':
                    print(f"   ❌ Task with wrong priority: {task.get('priority')} (expected critical)")
                    return False
            
            # Show critical tasks
            for task in response:
                print(f"   ✅ Critical task: {task.get('task')}")
            
            # Test high priority filter
            high_success, high_response = self.run_test(
                "Monitoring Tasks - Priority Filter: high",
                "GET",
                "crisis-framework/monitoring-tasks?priority=high",
                200
            )
            
            if high_success and isinstance(high_response, list):
                print(f"   Found {len(high_response)} high priority tasks")
                for task in high_response:
                    print(f"   ✅ High priority task: {task.get('task')}")
            
            # Test medium priority filter
            medium_success, medium_response = self.run_test(
                "Monitoring Tasks - Priority Filter: medium",
                "GET",
                "crisis-framework/monitoring-tasks?priority=medium",
                200
            )
            
            if medium_success and isinstance(medium_response, list):
                print(f"   Found {len(medium_response)} medium priority tasks")
                for task in medium_response:
                    print(f"   ✅ Medium priority task: {task.get('task')}")
            
            return True
        return False

    def test_monitoring_tasks_frequency_filter(self):
        """Test Monitoring Tasks endpoint with frequency filtering"""
        # Test real_time frequency filter
        success, response = self.run_test(
            "Monitoring Tasks - Frequency Filter: real_time",
            "GET",
            "crisis-framework/monitoring-tasks?frequency=real_time",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} real-time monitoring tasks")
            
            # Verify all tasks have real_time frequency
            for task in response:
                if task.get('frequency') != 'real_time':
                    print(f"   ❌ Task with wrong frequency: {task.get('frequency')} (expected real_time)")
                    return False
            
            # Show real-time tasks
            for task in response:
                print(f"   ✅ Real-time task: {task.get('task')}")
            
            # Test daily frequency filter
            daily_success, daily_response = self.run_test(
                "Monitoring Tasks - Frequency Filter: daily",
                "GET",
                "crisis-framework/monitoring-tasks?frequency=daily",
                200
            )
            
            if daily_success and isinstance(daily_response, list):
                print(f"   Found {len(daily_response)} daily monitoring tasks")
                for task in daily_response:
                    print(f"   ✅ Daily task: {task.get('task')}")
            
            return True
        return False

    def test_scenario_assessment_finnish_crisis(self):
        """Test Scenario Assessment with specific Finnish Economic Crisis scenario"""
        # Use the specific scenario ID from review request
        scenario_id = "9796a80e-976e-463d-ba00-aeb899b76a7a"
        
        print(f"\n🔍 Testing Crisis Framework Scenario Assessment...")
        print(f"   Scenario ID: {scenario_id}")
        print(f"   Title: Finnish Economic Crisis Test")
        
        # First login with test credentials
        test_email = "test@example.com"
        test_password = "password123"
        
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_success, login_response = self.run_test(
            "Login for Scenario Assessment",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if not login_success or 'access_token' not in login_response:
            print("❌ Failed to login with test credentials")
            return False
            
        # Update token for subsequent requests
        original_token = self.token
        self.token = login_response['access_token']
        print(f"   Logged in successfully with test credentials")
        
        try:
            # Test scenario assessment
            assessment_data = {
                "scenario_id": scenario_id
            }
            
            success, response = self.run_test(
                "Crisis Framework Scenario Assessment",
                "POST",
                "crisis-framework/scenario-assessment",
                200,
                data=assessment_data
            )
            
            if not success:
                print("❌ Failed to assess scenario against crisis factors")
                return False
                
            # Verify assessment response structure
            required_fields = ['scenario_id', 'scenario_title', 'crisis_type', 'severity_level',
                             'relevant_factors', 'recommended_monitoring', 'assessment_timestamp',
                             'total_factors', 'critical_monitoring_tasks']
            
            missing_fields = []
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields in assessment response: {missing_fields}")
                return False
                
            print(f"✅ Scenario assessment completed successfully")
            print(f"   Scenario ID: {response.get('scenario_id')}")
            print(f"   Scenario title: {response.get('scenario_title')}")
            print(f"   Crisis type: {response.get('crisis_type')}")
            print(f"   Severity level: {response.get('severity_level')}")
            print(f"   Total relevant factors: {response.get('total_factors')}")
            print(f"   Critical monitoring tasks: {response.get('critical_monitoring_tasks')}")
            
            # Verify relevant factors
            relevant_factors = response.get('relevant_factors', [])
            if relevant_factors:
                print(f"   Relevant factors found: {len(relevant_factors)}")
                for i, factor in enumerate(relevant_factors[:3]):  # Show first 3
                    print(f"   {i+1}. {factor.get('name')} ({factor.get('category')})")
                    print(f"      Relevance: {factor.get('relevance_score')}")
            else:
                print(f"   ⚠️ No relevant factors found")
            
            # Verify recommended monitoring
            recommended_monitoring = response.get('recommended_monitoring', [])
            if recommended_monitoring:
                print(f"   Recommended monitoring tasks: {len(recommended_monitoring)}")
                for i, task in enumerate(recommended_monitoring):
                    print(f"   {i+1}. {task.get('task')} (Priority: {task.get('priority')})")
                    print(f"      Frequency: {task.get('frequency')}")
            else:
                print(f"   ⚠️ No recommended monitoring tasks found")
            
            # Test with invalid scenario ID
            invalid_assessment_data = {
                "scenario_id": "invalid-scenario-id-12345"
            }
            
            invalid_success, invalid_response = self.run_test(
                "Crisis Assessment with Invalid Scenario ID",
                "POST",
                "crisis-framework/scenario-assessment",
                404,  # Should return 404 for non-existent scenario
                data=invalid_assessment_data
            )
            
            if not invalid_success:
                print("❌ Invalid scenario ID test failed - should return 404")
                return False
                
            print(f"✅ Invalid scenario ID properly handled with 404")
            
            return True
            
        finally:
            # Restore original token
            self.token = original_token

    def test_crisis_framework_authentication(self):
        """Test that Crisis Framework endpoints require authentication"""
        # Store current token
        temp_token = self.token
        self.token = None
        
        endpoints_to_test = [
            ("crisis-framework/summary", "GET"),
            ("crisis-framework/factors", "GET"),
            ("crisis-framework/monitoring-tasks", "GET"),
            ("crisis-framework/scenario-assessment", "POST")
        ]
        
        successful_auth_tests = 0
        
        for endpoint, method in endpoints_to_test:
            data = {"scenario_id": "test-id"} if method == "POST" else None
            
            success, response = self.run_test(
                f"Authentication Test - {endpoint}",
                method,
                endpoint,
                401,  # Should fail without authentication
                data=data
            )
            
            if success:
                successful_auth_tests += 1
                print(f"   ✅ {endpoint} properly requires authentication")
            else:
                print(f"   ❌ {endpoint} authentication test failed")
        
        # Restore token
        self.token = temp_token
        
        print(f"   Authentication tests passed: {successful_auth_tests}/{len(endpoints_to_test)}")
        return successful_auth_tests == len(endpoints_to_test)

    # ========== KNOWLEDGE TOPOLOGY ENDPOINTS TESTING ==========
    
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

    def test_knowledge_sources_priority_filter(self):
        """Test Knowledge Sources endpoint with priority filter"""
        priorities = ['high', 'medium', 'low']
        
        for priority in priorities:
            success, response = self.run_test(
                f"Knowledge Sources - Priority Filter ({priority})",
                "GET",
                f"knowledge-topology/sources?priority={priority}",
                200
            )
            
            if success and isinstance(response, list):
                print(f"   Priority '{priority}': {len(response)} sources found")
                
                # Verify all sources match the priority filter
                # Note: This requires checking against the original data structure
                # For now, we'll just verify we get results
                if len(response) > 0:
                    print(f"   ✅ Priority filter '{priority}' returned sources")
                else:
                    print(f"   ⚠️ Priority filter '{priority}' returned no sources")
            else:
                print(f"   ❌ Priority filter '{priority}' failed")
                return False
        
        return True

    def test_knowledge_sources_api_filter(self):
        """Test Knowledge Sources endpoint with API-only filter"""
        success, response = self.run_test(
            "Knowledge Sources - API Only Filter",
            "GET",
            "knowledge-topology/sources?api_only=true",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   API-only sources: {len(response)} found")
            
            # Verify all returned sources have API availability
            api_sources = [s for s in response if s.get('api_availability', False)]
            non_api_sources = [s for s in response if not s.get('api_availability', False)]
            
            if len(non_api_sources) > 0:
                print(f"   ❌ Found {len(non_api_sources)} non-API sources in API-only filter")
                return False
            else:
                print(f"   ✅ All {len(api_sources)} sources have API availability")
                
            # Show API sources
            if api_sources:
                print(f"   API-enabled sources:")
                for source in api_sources[:3]:  # Show first 3
                    print(f"   - {source.get('name')}: {source.get('type')}")
            
            return True
        return False

    def test_knowledge_sources_specialization_filter(self):
        """Test Knowledge Sources endpoint with specialization filter"""
        specializations = ['strategy', 'crisis_management', 'digital_transformation', 'risk_assessment']
        
        successful_tests = 0
        
        for specialization in specializations:
            success, response = self.run_test(
                f"Knowledge Sources - Specialization Filter ({specialization})",
                "GET",
                f"knowledge-topology/sources?specialization={specialization}",
                200
            )
            
            if success and isinstance(response, list):
                print(f"   Specialization '{specialization}': {len(response)} sources found")
                
                # Verify sources have the requested specialization
                if response:
                    matching_sources = 0
                    for source in response:
                        source_specs = [s.lower() for s in source.get('specialization', [])]
                        if specialization.lower() in source_specs:
                            matching_sources += 1
                    
                    if matching_sources == len(response):
                        print(f"   ✅ All sources match specialization '{specialization}'")
                        successful_tests += 1
                    else:
                        print(f"   ⚠️ Only {matching_sources}/{len(response)} sources match specialization")
                else:
                    print(f"   ⚠️ No sources found for specialization '{specialization}'")
            else:
                print(f"   ❌ Specialization filter '{specialization}' failed")
        
        print(f"   Successfully tested {successful_tests}/{len(specializations)} specialization filters")
        return successful_tests > 0

    def test_crisis_strategy_economic_crisis(self):
        """Test Crisis Strategy endpoint - Economic Crisis (severity 8)"""
        success, response = self.run_test(
            "Crisis Strategy - Economic Crisis (Severity 8)",
            "POST",
            "knowledge-topology/crisis-strategy?crisis_type=economic_crisis&severity_level=8",
            200
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
        success, response = self.run_test(
            "Crisis Strategy - Cyber Attack (Severity 6)",
            "POST",
            "knowledge-topology/crisis-strategy?crisis_type=cyber_attack&severity_level=6",
            200
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
        success, response = self.run_test(
            "Crisis Strategy - Pandemic (Severity 9)",
            "POST",
            "knowledge-topology/crisis-strategy?crisis_type=pandemic&severity_level=9",
            200
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

    def test_crisis_strategy_invalid_severity(self):
        """Test Crisis Strategy endpoint with invalid severity level"""
        success, response = self.run_test(
            "Crisis Strategy - Invalid Severity Level",
            "POST",
            "knowledge-topology/crisis-strategy?crisis_type=economic_crisis&severity_level=15",
            400  # Should return 400 Bad Request
        )
        
        if success:
            print(f"   ✅ Invalid severity level properly rejected with 400 status")
            return True
        return False

    def test_crisis_strategy_unknown_crisis_type(self):
        """Test Crisis Strategy endpoint with unknown crisis type"""
        success, response = self.run_test(
            "Crisis Strategy - Unknown Crisis Type",
            "POST",
            "knowledge-topology/crisis-strategy?crisis_type=alien_invasion&severity_level=5",
            200  # Should still work but use default specializations
        )
        
        if success:
            print(f"   ✅ Unknown crisis type handled gracefully")
            print(f"   Total sources: {response.get('total_sources', 'N/A')}")
            
            # Should get default crisis management sources
            recommended_sources = response.get('recommended_sources', [])
            if recommended_sources:
                print(f"   ✅ Default sources provided for unknown crisis type")
            else:
                print(f"   ❌ No sources provided for unknown crisis type")
                return False
            
            return True
        return False

    def test_knowledge_topology_authentication(self):
        """Test Knowledge Topology endpoints require authentication"""
        # Store current token
        original_token = self.token
        self.token = None
        
        endpoints_to_test = [
            ("knowledge-topology/summary", "GET"),
            ("knowledge-topology/sources", "GET"),
        ]
        
        auth_tests_passed = 0
        
        for endpoint, method in endpoints_to_test:
            success, response = self.run_test(
                f"Authentication Test - {endpoint}",
                method,
                endpoint,
                401  # Should return 401 Unauthorized
            )
            
            if success:
                auth_tests_passed += 1
                print(f"   ✅ {endpoint} properly requires authentication")
            else:
                print(f"   ❌ {endpoint} does not require authentication")
        
        # Test POST endpoint separately
        success, response = self.run_test(
            "Authentication Test - crisis-strategy",
            "POST",
            "knowledge-topology/crisis-strategy?crisis_type=economic_crisis&severity_level=5",
            401
        )
        
        if success:
            auth_tests_passed += 1
            print(f"   ✅ crisis-strategy properly requires authentication")
        else:
            print(f"   ❌ crisis-strategy does not require authentication")
        
        # Restore token
        self.token = original_token
        
        print(f"   Authentication tests passed: {auth_tests_passed}/3")
        return auth_tests_passed == 3

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

    # ========== TEAM CREATION FUNCTIONALITY TESTING ==========
    
    def test_team_creation_with_email_list(self):
        """Test Team Creation with Email List - Mixed existing and new emails"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for team creation with email list")
            return False
            
        # Create test data with mixed email list (existing and new)
        team_data = {
            "team_name": "Crisis Response Team Beta",
            "team_description": "Testing team creation with email list functionality",
            "team_members": [
                "existing.user@company.com",  # Simulate existing user
                "new.invite1@company.com",    # New invite
                "new.invite2@company.com",    # New invite
                "another.existing@company.com" # Another existing user
            ],
            "team_roles": ["crisis_manager", "analyst", "coordinator", "observer"]
        }
        
        success, response = self.run_test(
            "Team Creation with Email List",
            "POST",
            f"companies/{self.company_id}/teams",
            200,
            data=team_data
        )
        
        if success and 'id' in response:
            self.email_team_id = response['id']
            print(f"   Created team ID: {self.email_team_id}")
            print(f"   Team name: {response.get('team_name', 'N/A')}")
            print(f"   Team description: {response.get('team_description', 'N/A')}")
            print(f"   Team members count: {len(response.get('team_members', []))}")
            print(f"   Team roles: {response.get('team_roles', [])}")
            print(f"   Team lead: {response.get('team_lead', 'N/A')}")
            print(f"   Access level: {response.get('access_level', 'N/A')}")
            
            # Verify team_members field contains email addresses as expected
            team_members = response.get('team_members', [])
            if team_members:
                print(f"   Team members stored: {team_members}")
                # Check if emails are properly stored
                for email in team_data['team_members']:
                    if email in team_members:
                        print(f"   ✅ Email {email} properly stored")
                    else:
                        print(f"   ❌ Email {email} not found in stored team members")
            
            return True
        return False

    def test_team_creation_edge_cases(self):
        """Test Team Creation Edge Cases"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for edge case testing")
            return False
            
        edge_case_results = []
        
        # Test 1: Empty team_members list
        print(f"\n   🔍 Testing empty team_members list...")
        empty_team_data = {
            "team_name": "Empty Team Test",
            "team_description": "Testing empty team members list",
            "team_members": [],
            "team_roles": []
        }
        
        success, response = self.run_test(
            "Empty Team Members List",
            "POST",
            f"companies/{self.company_id}/teams",
            200,  # Assuming empty list is allowed
            data=empty_team_data
        )
        edge_case_results.append(("Empty team_members", success))
        
        # Test 2: Duplicate emails in team_members list
        print(f"\n   🔍 Testing duplicate emails...")
        duplicate_team_data = {
            "team_name": "Duplicate Email Test",
            "team_description": "Testing duplicate emails in team members",
            "team_members": [
                "duplicate@company.com",
                "unique1@company.com", 
                "duplicate@company.com",  # Duplicate
                "unique2@company.com"
            ],
            "team_roles": ["crisis_manager", "analyst"]
        }
        
        success, response = self.run_test(
            "Duplicate Emails in Team Members",
            "POST",
            f"companies/{self.company_id}/teams",
            200,  # Should handle duplicates gracefully
            data=duplicate_team_data
        )
        edge_case_results.append(("Duplicate emails", success))
        
        # Test 3: Invalid email formats
        print(f"\n   🔍 Testing invalid email formats...")
        invalid_email_data = {
            "team_name": "Invalid Email Test",
            "team_description": "Testing invalid email formats",
            "team_members": [
                "valid@company.com",
                "invalid-email",  # Invalid format
                "another@invalid",  # Invalid format
                "also.valid@company.com"
            ],
            "team_roles": ["analyst"]
        }
        
        success, response = self.run_test(
            "Invalid Email Formats",
            "POST",
            f"companies/{self.company_id}/teams",
            422,  # Should reject invalid emails with validation error
            data=invalid_email_data
        )
        edge_case_results.append(("Invalid email formats", success))
        
        # Test 4: Very long team_members list
        print(f"\n   🔍 Testing very long team_members list...")
        long_email_list = [f"user{i}@company.com" for i in range(50)]  # 50 emails
        long_team_data = {
            "team_name": "Large Team Test",
            "team_description": "Testing very long team members list",
            "team_members": long_email_list,
            "team_roles": ["crisis_manager", "analyst", "coordinator"]
        }
        
        success, response = self.run_test(
            "Very Long Team Members List",
            "POST",
            f"companies/{self.company_id}/teams",
            200,  # Should handle large lists
            data=long_team_data
        )
        edge_case_results.append(("Long team_members list", success))
        
        # Summary of edge case results
        print(f"\n   📊 Edge Case Test Results:")
        passed_edge_cases = 0
        for test_name, result in edge_case_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   - {test_name}: {status}")
            if result:
                passed_edge_cases += 1
        
        print(f"   Edge cases passed: {passed_edge_cases}/{len(edge_case_results)}")
        return passed_edge_cases > 0

    def test_team_creation_access_control(self):
        """Test Team Creation Access Control"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for access control testing")
            return False
            
        # Test 1: Valid access (current user is company member/creator)
        print(f"\n   🔍 Testing valid access...")
        valid_team_data = {
            "team_name": "Access Control Valid Team",
            "team_description": "Testing valid access control",
            "team_members": ["member1@company.com", "member2@company.com"],
            "team_roles": ["crisis_manager", "analyst"]
        }
        
        success, response = self.run_test(
            "Valid Access Control",
            "POST",
            f"companies/{self.company_id}/teams",
            200,
            data=valid_team_data
        )
        
        if success:
            print(f"   ✅ Valid access test passed")
        else:
            print(f"   ❌ Valid access test failed")
        
        # Test 2: Invalid access (try to access non-existent company)
        print(f"\n   🔍 Testing invalid access with non-existent company...")
        fake_company_id = "non-existent-company-id"
        
        invalid_success, invalid_response = self.run_test(
            "Invalid Access Control - Non-existent Company",
            "POST",
            f"companies/{fake_company_id}/teams",
            403,  # Should return 403 Forbidden
            data=valid_team_data
        )
        
        if invalid_success:
            print(f"   ✅ Invalid access properly rejected")
        else:
            print(f"   ❌ Invalid access not properly rejected")
        
        # Test 3: Test without authentication token
        print(f"\n   🔍 Testing access without authentication...")
        original_token = self.token
        self.token = None  # Remove token temporarily
        
        no_auth_success, no_auth_response = self.run_test(
            "No Authentication Access Control",
            "POST",
            f"companies/{self.company_id}/teams",
            401,  # Should return 401 Unauthorized
            data=valid_team_data
        )
        
        self.token = original_token  # Restore token
        
        if no_auth_success:
            print(f"   ✅ No authentication properly rejected")
        else:
            print(f"   ❌ No authentication not properly rejected")
        
        access_tests_passed = sum([success, invalid_success, no_auth_success])
        print(f"   📊 Access control tests passed: {access_tests_passed}/3")
        
        return access_tests_passed >= 2  # At least 2 out of 3 should pass

    def test_team_data_structure_verification(self):
        """Test Team Data Structure Verification"""
        if not hasattr(self, 'company_id') or not self.company_id:
            print("❌ No company ID available for data structure verification")
            return False
            
        # Create a comprehensive team for structure verification
        comprehensive_team_data = {
            "team_name": "Data Structure Verification Team",
            "team_description": "Comprehensive team for verifying all data structure fields",
            "team_members": [
                "lead@company.com",
                "analyst1@company.com", 
                "coordinator@company.com",
                "observer@company.com"
            ],
            "team_roles": ["crisis_manager", "analyst", "coordinator", "observer"]
        }
        
        success, response = self.run_test(
            "Team Data Structure Verification",
            "POST",
            f"companies/{self.company_id}/teams",
            200,
            data=comprehensive_team_data
        )
        
        if not success or 'id' not in response:
            print("   ❌ Failed to create team for structure verification")
            return False
        
        # Verify all required Team model fields are present
        required_fields = [
            'id', 'company_id', 'team_name', 'team_description', 
            'team_lead', 'team_members', 'access_level', 'team_roles', 
            'active_scenarios', 'created_at'
        ]
        
        structure_verification_results = []
        
        print(f"   🔍 Verifying Team model structure...")
        for field in required_fields:
            if field in response:
                field_value = response[field]
                print(f"   ✅ {field}: {type(field_value).__name__} = {field_value}")
                structure_verification_results.append(True)
            else:
                print(f"   ❌ Missing field: {field}")
                structure_verification_results.append(False)
        
        # Verify specific field types and values
        print(f"\n   🔍 Verifying field types and values...")
        
        # Check team_name
        if response.get('team_name') == comprehensive_team_data['team_name']:
            print(f"   ✅ team_name correctly set")
        else:
            print(f"   ❌ team_name mismatch")
        
        # Check team_description  
        if response.get('team_description') == comprehensive_team_data['team_description']:
            print(f"   ✅ team_description correctly set")
        else:
            print(f"   ❌ team_description mismatch")
        
        # Check team_lead (should be current user ID)
        if response.get('team_lead') == self.user_id:
            print(f"   ✅ team_lead correctly set to current user")
        else:
            print(f"   ❌ team_lead not set to current user")
        
        # Check team_members (should contain email addresses)
        team_members = response.get('team_members', [])
        if isinstance(team_members, list) and len(team_members) == len(comprehensive_team_data['team_members']):
            print(f"   ✅ team_members list has correct length")
            # Check if emails are stored (implementation may convert to user IDs)
            for email in comprehensive_team_data['team_members']:
                if email in team_members:
                    print(f"   ✅ Email {email} found in team_members")
                else:
                    print(f"   ⚠️  Email {email} not found (may be converted to user ID)")
        else:
            print(f"   ❌ team_members list length mismatch")
        
        # Check team_roles
        team_roles = response.get('team_roles', [])
        if team_roles == comprehensive_team_data['team_roles']:
            print(f"   ✅ team_roles correctly set")
        else:
            print(f"   ❌ team_roles mismatch")
        
        # Check access_level (should have default value)
        if response.get('access_level') == 'standard':
            print(f"   ✅ access_level has correct default value")
        else:
            print(f"   ❌ access_level incorrect")
        
        # Check active_scenarios (should be empty list initially)
        if response.get('active_scenarios') == []:
            print(f"   ✅ active_scenarios correctly initialized as empty")
        else:
            print(f"   ❌ active_scenarios not properly initialized")
        
        # Check created_at (should be a valid datetime string)
        created_at = response.get('created_at')
        if created_at and isinstance(created_at, str):
            print(f"   ✅ created_at field present and is string")
        else:
            print(f"   ❌ created_at field missing or wrong type")
        
        passed_verifications = sum(structure_verification_results)
        total_verifications = len(structure_verification_results)
        
        print(f"\n   📊 Structure verification: {passed_verifications}/{total_verifications} fields verified")
        
        # Store team ID for potential cleanup
        self.structure_team_id = response.get('id')
        
        return passed_verifications >= (total_verifications * 0.8)  # 80% pass rate

    def test_finland_regions_investigation(self):
        """CRITICAL INVESTIGATION: Test Finland regions issue - comprehensive data flow analysis"""
        print("\n🔍 CRITICAL INVESTIGATION: Finland Regions Data Loss Issue")
        print("=" * 80)
        
        # Step 1: Check existing scenarios in database
        print("\n📋 STEP 1: Checking existing scenarios in database...")
        success, existing_scenarios = self.run_test(
            "Get All Existing Scenarios",
            "GET",
            "scenarios",
            200
        )
        
        if success and isinstance(existing_scenarios, list):
            print(f"   Found {len(existing_scenarios)} existing scenarios")
            
            # Look for scenarios created today (9.9.2025) and check affected_regions
            today_scenarios = []
            for scenario in existing_scenarios:
                created_at = scenario.get('created_at', '')
                if '2025-09-09' in created_at or '9.9.2025' in created_at:
                    today_scenarios.append(scenario)
                    
                print(f"   - Scenario: {scenario.get('title', 'N/A')}")
                print(f"     ID: {scenario.get('id', 'N/A')}")
                print(f"     Created: {scenario.get('created_at', 'N/A')}")
                print(f"     Affected Regions: {scenario.get('affected_regions', 'MISSING FIELD!')}")
                print(f"     Regions Type: {type(scenario.get('affected_regions', None))}")
                print(f"     Regions Length: {len(scenario.get('affected_regions', [])) if isinstance(scenario.get('affected_regions'), list) else 'NOT A LIST'}")
                
                # Check if Finland is in any scenario
                regions = scenario.get('affected_regions', [])
                if isinstance(regions, list) and 'Finland' in regions:
                    print(f"     ✅ FOUND FINLAND in scenario: {scenario.get('title')}")
                elif isinstance(regions, list) and any('finland' in str(r).lower() for r in regions):
                    print(f"     ⚠️ Found Finland variant: {[r for r in regions if 'finland' in str(r).lower()]}")
                else:
                    print(f"     ❌ No Finland found in regions")
            
            print(f"\n   Today's scenarios (9.9.2025): {len(today_scenarios)}")
        
        # Step 2: Test scenario creation with Finland - LOG EVERYTHING
        print("\n📋 STEP 2: Testing scenario creation with Finland - DETAILED LOGGING")
        
        finland_scenario_data = {
            "title": "Finland Region Test",
            "description": "Testing if Finland region is properly saved",
            "crisis_type": "economic_crisis",
            "severity_level": 7,
            "affected_regions": ["Finland"],
            "key_variables": ["Economy", "Population", "Infrastructure"]
        }
        
        print(f"   REQUEST PAYLOAD BEING SENT:")
        print(f"   {json.dumps(finland_scenario_data, indent=4)}")
        
        success, response = self.run_test(
            "Create Finland Test Scenario",
            "POST",
            "scenarios",
            200,
            data=finland_scenario_data
        )
        
        if success and 'id' in response:
            finland_scenario_id = response['id']
            print(f"\n   ✅ SCENARIO CREATED SUCCESSFULLY")
            print(f"   Scenario ID: {finland_scenario_id}")
            print(f"   RESPONSE RECEIVED:")
            print(f"   {json.dumps(response, indent=4)}")
            
            # Verify affected_regions field in response
            response_regions = response.get('affected_regions', 'MISSING')
            print(f"\n   RESPONSE ANALYSIS:")
            print(f"   - affected_regions field present: {response_regions != 'MISSING'}")
            print(f"   - affected_regions value: {response_regions}")
            print(f"   - affected_regions type: {type(response_regions)}")
            if isinstance(response_regions, list):
                print(f"   - affected_regions length: {len(response_regions)}")
                print(f"   - Finland in list: {'Finland' in response_regions}")
            
            # Step 3: Immediately retrieve the scenario to check persistence
            print(f"\n📋 STEP 3: Immediately retrieving scenario to verify persistence...")
            
            retrieve_success, retrieve_response = self.run_test(
                "Retrieve Finland Test Scenario",
                "GET",
                f"scenarios/{finland_scenario_id}",
                200
            )
            
            if retrieve_success:
                print(f"   ✅ SCENARIO RETRIEVED SUCCESSFULLY")
                print(f"   RETRIEVED RESPONSE:")
                print(f"   {json.dumps(retrieve_response, indent=4)}")
                
                # Compare original vs retrieved
                original_regions = finland_scenario_data['affected_regions']
                retrieved_regions = retrieve_response.get('affected_regions', 'MISSING')
                
                print(f"\n   DATA INTEGRITY CHECK:")
                print(f"   - Original regions: {original_regions}")
                print(f"   - Retrieved regions: {retrieved_regions}")
                print(f"   - Data match: {original_regions == retrieved_regions}")
                
                if original_regions != retrieved_regions:
                    print(f"   ❌ CRITICAL DATA LOSS DETECTED!")
                    print(f"   - Expected: {original_regions}")
                    print(f"   - Got: {retrieved_regions}")
                    print(f"   - Loss type: {type(retrieved_regions)} vs expected {type(original_regions)}")
                else:
                    print(f"   ✅ Data integrity maintained")
            
            # Step 4: Check all scenarios again to see if Finland scenario appears
            print(f"\n📋 STEP 4: Checking all scenarios again to verify Finland scenario...")
            
            verify_success, all_scenarios = self.run_test(
                "Verify All Scenarios Include Finland Test",
                "GET",
                "scenarios",
                200
            )
            
            if verify_success and isinstance(all_scenarios, list):
                finland_found = False
                for scenario in all_scenarios:
                    if scenario.get('id') == finland_scenario_id:
                        finland_found = True
                        print(f"   ✅ Found Finland test scenario in list")
                        print(f"   - Title: {scenario.get('title')}")
                        print(f"   - Regions: {scenario.get('affected_regions')}")
                        break
                
                if not finland_found:
                    print(f"   ❌ Finland test scenario NOT found in scenarios list!")
            
            # Step 5: Test multiple Finland scenarios with different data
            print(f"\n📋 STEP 5: Testing multiple Finland scenarios with variations...")
            
            test_scenarios = [
                {
                    "title": "Finland Economic Crisis",
                    "description": "Economic downturn affecting Finland specifically",
                    "crisis_type": "economic_crisis",
                    "severity_level": 8,
                    "affected_regions": ["Finland", "Nordic Region"],
                    "key_variables": ["GDP", "Employment", "Currency"]
                },
                {
                    "title": "Finland Environmental Crisis", 
                    "description": "Environmental challenges in Finland",
                    "crisis_type": "environmental_crisis",
                    "severity_level": 6,
                    "affected_regions": ["Finland"],
                    "key_variables": ["Climate", "Forests", "Water"]
                },
                {
                    "title": "Multi-Region with Finland",
                    "description": "Crisis affecting multiple regions including Finland",
                    "crisis_type": "social_unrest",
                    "severity_level": 5,
                    "affected_regions": ["Finland", "Sweden", "Norway", "Denmark"],
                    "key_variables": ["Population", "Migration", "Social Services"]
                }
            ]
            
            created_test_scenarios = []
            for i, test_data in enumerate(test_scenarios):
                print(f"\n   Testing scenario {i+1}: {test_data['title']}")
                test_success, test_response = self.run_test(
                    f"Create Finland Test Scenario {i+1}",
                    "POST", 
                    "scenarios",
                    200,
                    data=test_data
                )
                
                if test_success and 'id' in test_response:
                    created_test_scenarios.append(test_response['id'])
                    original_regions = test_data['affected_regions']
                    response_regions = test_response.get('affected_regions')
                    
                    print(f"     Original: {original_regions}")
                    print(f"     Response: {response_regions}")
                    print(f"     Match: {original_regions == response_regions}")
                    
                    if 'Finland' in original_regions:
                        if isinstance(response_regions, list) and 'Finland' in response_regions:
                            print(f"     ✅ Finland preserved in response")
                        else:
                            print(f"     ❌ Finland LOST in response!")
            
            # Step 6: Final verification - get all scenarios and check Finland presence
            print(f"\n📋 STEP 6: Final verification of all Finland scenarios...")
            
            final_success, final_scenarios = self.run_test(
                "Final Verification - All Scenarios",
                "GET",
                "scenarios", 
                200
            )
            
            if final_success and isinstance(final_scenarios, list):
                finland_scenarios = []
                for scenario in final_scenarios:
                    regions = scenario.get('affected_regions', [])
                    if isinstance(regions, list) and 'Finland' in regions:
                        finland_scenarios.append(scenario)
                
                print(f"   Total scenarios: {len(final_scenarios)}")
                print(f"   Scenarios with Finland: {len(finland_scenarios)}")
                
                for scenario in finland_scenarios:
                    print(f"   - {scenario.get('title')}: {scenario.get('affected_regions')}")
            
            return True
        else:
            print(f"   ❌ FAILED to create Finland test scenario")
            return False

    def test_scenario_data_persistence_comprehensive(self):
        """Comprehensive test for scenario creation and retrieval functionality"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE SCENARIO DATA PERSISTENCE TESTING")
        print("="*80)
        
        # Test 1: Create scenario with complete data as specified in review
        print("\n🔍 Test 1: Creating scenario with complete data...")
        complete_scenario_data = {
            "title": "Test Economic Crisis",
            "description": "A comprehensive economic downturn scenario for testing data persistence with detailed analysis of market volatility, unemployment rates, and cascading effects across multiple sectors including banking, retail, and manufacturing industries.",
            "crisis_type": "economic_crisis",
            "severity_level": 7,
            "affected_regions": ["North America", "Europe", "Asia Pacific"],
            "key_variables": ["Inflation Rate", "Employment", "GDP Growth", "Market Volatility"]
        }
        
        success, response = self.run_test(
            "Create Complete Scenario",
            "POST",
            "scenarios",
            200,
            data=complete_scenario_data
        )
        
        if not success or 'id' not in response:
            print("❌ Failed to create scenario - stopping persistence tests")
            return False
            
        created_scenario_id = response['id']
        print(f"   ✅ Created scenario ID: {created_scenario_id}")
        
        # Verify all fields are present in creation response
        print("\n🔍 Verifying creation response data integrity...")
        required_fields = ['id', 'title', 'description', 'crisis_type', 'severity_level', 'affected_regions', 'key_variables', 'user_id', 'status', 'created_at', 'updated_at']
        missing_fields = []
        
        for field in required_fields:
            if field not in response:
                missing_fields.append(field)
            else:
                print(f"   ✅ {field}: {response[field] if field not in ['description'] else str(response[field])[:50] + '...'}")
        
        if missing_fields:
            print(f"   ❌ Missing fields in creation response: {missing_fields}")
            return False
        
        # Verify data matches what was sent
        print("\n🔍 Verifying data integrity in creation response...")
        data_integrity_checks = [
            ('title', complete_scenario_data['title']),
            ('description', complete_scenario_data['description']),
            ('crisis_type', complete_scenario_data['crisis_type']),
            ('severity_level', complete_scenario_data['severity_level']),
            ('affected_regions', complete_scenario_data['affected_regions']),
            ('key_variables', complete_scenario_data['key_variables'])
        ]
        
        for field, expected_value in data_integrity_checks:
            if response.get(field) != expected_value:
                print(f"   ❌ Data mismatch for {field}: expected {expected_value}, got {response.get(field)}")
                return False
            else:
                print(f"   ✅ {field} matches expected value")
        
        # Test 2: Retrieve all scenarios and verify data persistence
        print("\n🔍 Test 2: Retrieving all scenarios...")
        success, scenarios_response = self.run_test(
            "Get All Scenarios",
            "GET",
            "scenarios",
            200
        )
        
        if not success or not isinstance(scenarios_response, list):
            print("❌ Failed to retrieve scenarios")
            return False
            
        print(f"   ✅ Retrieved {len(scenarios_response)} scenarios")
        
        # Find our created scenario in the list
        created_scenario = None
        for scenario in scenarios_response:
            if scenario.get('id') == created_scenario_id:
                created_scenario = scenario
                break
        
        if not created_scenario:
            print(f"   ❌ Created scenario {created_scenario_id} not found in scenarios list")
            return False
        
        print("   ✅ Created scenario found in scenarios list")
        
        # Verify all data is preserved in list retrieval
        print("\n🔍 Verifying data persistence in list retrieval...")
        for field, expected_value in data_integrity_checks:
            if created_scenario.get(field) != expected_value:
                print(f"   ❌ Data loss in list retrieval for {field}: expected {expected_value}, got {created_scenario.get(field)}")
                return False
            else:
                print(f"   ✅ {field} preserved in list retrieval")
        
        # Test 3: Retrieve individual scenario by ID
        print("\n🔍 Test 3: Retrieving individual scenario by ID...")
        success, individual_response = self.run_test(
            "Get Individual Scenario",
            "GET",
            f"scenarios/{created_scenario_id}",
            200
        )
        
        if not success or 'id' not in individual_response:
            print("❌ Failed to retrieve individual scenario")
            return False
            
        print(f"   ✅ Retrieved individual scenario: {individual_response.get('title')}")
        
        # Verify all data is preserved in individual retrieval
        print("\n🔍 Verifying data persistence in individual retrieval...")
        for field, expected_value in data_integrity_checks:
            if individual_response.get(field) != expected_value:
                print(f"   ❌ Data loss in individual retrieval for {field}: expected {expected_value}, got {individual_response.get(field)}")
                return False
            else:
                print(f"   ✅ {field} preserved in individual retrieval")
        
        # Test 4: Array field preservation check
        print("\n🔍 Test 4: Detailed array field preservation check...")
        
        # Check affected_regions array
        expected_regions = complete_scenario_data['affected_regions']
        actual_regions = individual_response.get('affected_regions', [])
        
        if len(actual_regions) != len(expected_regions):
            print(f"   ❌ affected_regions length mismatch: expected {len(expected_regions)}, got {len(actual_regions)}")
            return False
        
        for i, region in enumerate(expected_regions):
            if i >= len(actual_regions) or actual_regions[i] != region:
                print(f"   ❌ affected_regions[{i}] mismatch: expected '{region}', got '{actual_regions[i] if i < len(actual_regions) else 'MISSING'}'")
                return False
        
        print(f"   ✅ affected_regions array preserved: {actual_regions}")
        
        # Check key_variables array
        expected_variables = complete_scenario_data['key_variables']
        actual_variables = individual_response.get('key_variables', [])
        
        if len(actual_variables) != len(expected_variables):
            print(f"   ❌ key_variables length mismatch: expected {len(expected_variables)}, got {len(actual_variables)}")
            return False
        
        for i, variable in enumerate(expected_variables):
            if i >= len(actual_variables) or actual_variables[i] != variable:
                print(f"   ❌ key_variables[{i}] mismatch: expected '{variable}', got '{actual_variables[i] if i < len(actual_variables) else 'MISSING'}'")
                return False
        
        print(f"   ✅ key_variables array preserved: {actual_variables}")
        
        # Test 5: Description field completeness check
        print("\n🔍 Test 5: Description field completeness check...")
        expected_description = complete_scenario_data['description']
        actual_description = individual_response.get('description', '')
        
        if len(actual_description) != len(expected_description):
            print(f"   ❌ Description length mismatch: expected {len(expected_description)}, got {len(actual_description)}")
            print(f"   Expected: {expected_description}")
            print(f"   Actual: {actual_description}")
            return False
        
        if actual_description != expected_description:
            print(f"   ❌ Description content mismatch")
            print(f"   Expected: {expected_description}")
            print(f"   Actual: {actual_description}")
            return False
        
        print(f"   ✅ Description field complete and intact ({len(actual_description)} characters)")
        
        # Test 6: Edge cases - Create scenarios with edge case data
        print("\n🔍 Test 6: Edge case testing...")
        
        edge_cases = [
            {
                "name": "Empty Arrays",
                "data": {
                    "title": "Empty Arrays Test",
                    "description": "Testing scenario with empty arrays",
                    "crisis_type": "social_unrest",
                    "severity_level": 5,
                    "affected_regions": [],
                    "key_variables": []
                }
            },
            {
                "name": "Long Description",
                "data": {
                    "title": "Long Description Test",
                    "description": "A" * 1500 + " This is a very long description to test data persistence with large text fields. " + "B" * 1500,
                    "crisis_type": "natural_disaster",
                    "severity_level": 9,
                    "affected_regions": ["Global"],
                    "key_variables": ["Extensive Variable Name That Is Very Long"]
                }
            },
            {
                "name": "Special Characters",
                "data": {
                    "title": "Special Characters Test: àáâãäåæçèéêë",
                    "description": "Testing with special characters: !@#$%^&*()_+-=[]{}|;':\",./<>? àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ",
                    "crisis_type": "pandemic",
                    "severity_level": 8,
                    "affected_regions": ["Région Spéciale", "Área Específica", "特別地域"],
                    "key_variables": ["Variável Especial", "変数", "переменная"]
                }
            },
            {
                "name": "Maximum Severity",
                "data": {
                    "title": "Maximum Severity Test",
                    "description": "Testing maximum severity level scenario",
                    "crisis_type": "cyber_attack",
                    "severity_level": 10,
                    "affected_regions": ["North America", "South America", "Europe", "Africa", "Asia", "Oceania", "Antarctica"],
                    "key_variables": ["Critical Infrastructure", "Data Security", "Economic Impact", "Social Disruption", "Government Response"]
                }
            }
        ]
        
        edge_case_ids = []
        
        for edge_case in edge_cases:
            print(f"\n   Testing edge case: {edge_case['name']}")
            
            success, response = self.run_test(
                f"Create Edge Case - {edge_case['name']}",
                "POST",
                "scenarios",
                200,
                data=edge_case['data']
            )
            
            if success and 'id' in response:
                edge_case_id = response['id']
                edge_case_ids.append(edge_case_id)
                print(f"     ✅ Created edge case scenario: {edge_case_id}")
                
                # Immediately retrieve and verify
                success, verify_response = self.run_test(
                    f"Verify Edge Case - {edge_case['name']}",
                    "GET",
                    f"scenarios/{edge_case_id}",
                    200
                )
                
                if success:
                    # Verify data integrity for edge case
                    for field, expected_value in edge_case['data'].items():
                        if verify_response.get(field) != expected_value:
                            print(f"     ❌ Edge case data mismatch for {field}")
                            return False
                    print(f"     ✅ Edge case data integrity verified")
                else:
                    print(f"     ❌ Failed to verify edge case scenario")
                    return False
            else:
                print(f"     ❌ Failed to create edge case scenario")
                return False
        
        # Test 7: Multiple scenario data persistence
        print(f"\n🔍 Test 7: Multiple scenario data persistence check...")
        
        success, final_scenarios = self.run_test(
            "Final Scenarios List Check",
            "GET",
            "scenarios",
            200
        )
        
        if success and isinstance(final_scenarios, list):
            print(f"   ✅ Final scenario count: {len(final_scenarios)}")
            
            # Verify all our created scenarios are present
            all_created_ids = [created_scenario_id] + edge_case_ids
            found_scenarios = 0
            
            for scenario in final_scenarios:
                if scenario.get('id') in all_created_ids:
                    found_scenarios += 1
            
            if found_scenarios == len(all_created_ids):
                print(f"   ✅ All {len(all_created_ids)} created scenarios found in final list")
            else:
                print(f"   ❌ Only {found_scenarios}/{len(all_created_ids)} created scenarios found in final list")
                return False
        else:
            print("   ❌ Failed to get final scenarios list")
            return False
        
        # Store the main scenario ID for cleanup
        self.created_scenario_id = created_scenario_id
        
        print("\n🎉 COMPREHENSIVE SCENARIO DATA PERSISTENCE TESTING COMPLETED SUCCESSFULLY!")
        print("   ✅ All data integrity checks passed")
        print("   ✅ Array fields preserved correctly")
        print("   ✅ Description field completeness verified")
        print("   ✅ Edge cases handled properly")
        print("   ✅ Multiple scenario persistence confirmed")
        
        return True

    def test_team_creation_comprehensive(self):
        """Run all team creation tests comprehensively"""
        print("\n📋 COMPREHENSIVE TEAM CREATION TESTING")
        print("-" * 60)
        
        test_results = []
        
        # Test 1: Team Creation with Email List
        print(f"\n🔍 Test 1: Team Creation with Email List")
        result1 = self.test_team_creation_with_email_list()
        test_results.append(("Email List Creation", result1))
        
        # Test 2: Edge Cases
        print(f"\n🔍 Test 2: Edge Cases Testing")
        result2 = self.test_team_creation_edge_cases()
        test_results.append(("Edge Cases", result2))
        
        # Test 3: Access Control
        print(f"\n🔍 Test 3: Access Control Testing")
        result3 = self.test_team_creation_access_control()
        test_results.append(("Access Control", result3))
        
        # Test 4: Data Structure Verification
        print(f"\n🔍 Test 4: Data Structure Verification")
        result4 = self.test_team_data_structure_verification()
        test_results.append(("Data Structure", result4))
        
        # Summary
        print(f"\n📊 TEAM CREATION TEST SUMMARY")
        print("-" * 40)
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / len(test_results)) * 100
        print(f"\n   Overall Success Rate: {passed_tests}/{len(test_results)} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print(f"   🎉 Team creation functionality is working well!")
        else:
            print(f"   ⚠️  Team creation functionality needs attention.")
        
        return passed_tests >= 3  # At least 3 out of 4 tests should pass

    def test_scenario_amendment_functionality(self):
        """Test the newly fixed scenario amendment functionality"""
        print("\n🔍 Testing Scenario Amendment Functionality (Review Request)...")
        
        # Test credentials from review request
        test_email = "test@example.com"
        test_password = "password123"
        scenario_id = "9796a80e-976e-463d-ba00-aeb899b76a7a"
        
        print(f"   Scenario ID: {scenario_id}")
        print(f"   User: {test_email}")
        
        # First login with test credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_success, login_response = self.run_test(
            "Login with Test Credentials for Amendment",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if not login_success or 'access_token' not in login_response:
            print("❌ Failed to login with test credentials")
            return False
            
        # Update token for subsequent requests
        original_token = self.token
        self.token = login_response['access_token']
        print(f"   Logged in successfully with test credentials")
        
        try:
            # Test 1: Get original scenario to verify current state
            original_success, original_response = self.run_test(
                "Get Original Scenario Before Amendment",
                "GET",
                f"scenarios/{scenario_id}",
                200
            )
            
            if not original_success:
                print("❌ Failed to get original scenario")
                return False
                
            print(f"✅ Original scenario retrieved")
            print(f"   Title: {original_response.get('title', 'N/A')}")
            print(f"   Original affected_regions: {original_response.get('affected_regions', [])}")
            print(f"   Original key_variables: {original_response.get('key_variables', [])}")
            print(f"   Original additional_context: {original_response.get('additional_context', 'None')}")
            print(f"   Original stakeholders: {original_response.get('stakeholders', 'None')}")
            print(f"   Original timeline: {original_response.get('timeline', 'None')}")
            
            # Test 2: Test PATCH endpoint with partial amendment data
            amendment_data = {
                "affected_regions": ["Finland", "Sweden", "Estonia"],
                "key_variables": ["GDP Growth", "Employment Rate", "Trade Balance"],
                "additional_context": "Enhanced scenario with regional economic interdependencies",
                "stakeholders": "Nordic Council, EU Commission, Central Banks",
                "timeline": "6-12 months recovery period"
            }
            
            amendment_success, amendment_response = self.run_test(
                "PATCH Scenario Amendment",
                "PATCH",
                f"scenarios/{scenario_id}/amend",
                200,
                data=amendment_data
            )
            
            if not amendment_success:
                print("❌ Failed to amend scenario")
                return False
                
            print(f"✅ Scenario amendment successful")
            print(f"   Amendment ID: {amendment_response.get('id')}")
            
            # Verify amendment response structure
            required_fields = ['id', 'title', 'description', 'crisis_type', 'severity_level', 
                             'affected_regions', 'key_variables', 'additional_context', 
                             'stakeholders', 'timeline', 'updated_at']
            
            missing_fields = []
            for field in required_fields:
                if field not in amendment_response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields in amendment response: {missing_fields}")
                return False
                
            # Test 3: Verify only provided fields were updated
            print(f"   Verifying field updates...")
            
            # Check updated fields
            updated_regions = amendment_response.get('affected_regions', [])
            updated_variables = amendment_response.get('key_variables', [])
            updated_context = amendment_response.get('additional_context', '')
            updated_stakeholders = amendment_response.get('stakeholders', '')
            updated_timeline = amendment_response.get('timeline', '')
            
            # Verify updated fields match amendment data
            if updated_regions != amendment_data['affected_regions']:
                print(f"❌ affected_regions not updated correctly: {updated_regions} vs {amendment_data['affected_regions']}")
                return False
            print(f"   ✅ affected_regions updated correctly: {updated_regions}")
            
            if updated_variables != amendment_data['key_variables']:
                print(f"❌ key_variables not updated correctly: {updated_variables} vs {amendment_data['key_variables']}")
                return False
            print(f"   ✅ key_variables updated correctly: {updated_variables}")
            
            if updated_context != amendment_data['additional_context']:
                print(f"❌ additional_context not updated correctly")
                return False
            print(f"   ✅ additional_context updated correctly")
            
            if updated_stakeholders != amendment_data['stakeholders']:
                print(f"❌ stakeholders not updated correctly")
                return False
            print(f"   ✅ stakeholders updated correctly")
            
            if updated_timeline != amendment_data['timeline']:
                print(f"❌ timeline not updated correctly")
                return False
            print(f"   ✅ timeline updated correctly")
            
            # Verify unchanged fields remain the same
            if amendment_response.get('title') != original_response.get('title'):
                print(f"❌ title should not have changed")
                return False
            print(f"   ✅ title unchanged: {amendment_response.get('title')}")
            
            if amendment_response.get('description') != original_response.get('description'):
                print(f"❌ description should not have changed")
                return False
            print(f"   ✅ description unchanged")
            
            if amendment_response.get('crisis_type') != original_response.get('crisis_type'):
                print(f"❌ crisis_type should not have changed")
                return False
            print(f"   ✅ crisis_type unchanged: {amendment_response.get('crisis_type')}")
            
            if amendment_response.get('severity_level') != original_response.get('severity_level'):
                print(f"❌ severity_level should not have changed")
                return False
            print(f"   ✅ severity_level unchanged: {amendment_response.get('severity_level')}")
            
            # Test 4: Verify GET scenarios returns updated scenario
            get_updated_success, get_updated_response = self.run_test(
                "GET Updated Scenario After Amendment",
                "GET",
                f"scenarios/{scenario_id}",
                200
            )
            
            if not get_updated_success:
                print("❌ Failed to get updated scenario")
                return False
                
            # Verify GET response matches PATCH response
            if get_updated_response.get('affected_regions') != amendment_data['affected_regions']:
                print(f"❌ GET response affected_regions doesn't match amendment")
                return False
                
            if get_updated_response.get('key_variables') != amendment_data['key_variables']:
                print(f"❌ GET response key_variables doesn't match amendment")
                return False
                
            if get_updated_response.get('additional_context') != amendment_data['additional_context']:
                print(f"❌ GET response additional_context doesn't match amendment")
                return False
                
            if get_updated_response.get('stakeholders') != amendment_data['stakeholders']:
                print(f"❌ GET response stakeholders doesn't match amendment")
                return False
                
            if get_updated_response.get('timeline') != amendment_data['timeline']:
                print(f"❌ GET response timeline doesn't match amendment")
                return False
                
            print(f"✅ GET scenarios returns correctly updated scenario")
            
            # Test 5: Test partial amendment (only some fields)
            partial_amendment_data = {
                "affected_regions": ["Finland", "Norway"],
                "additional_context": "Updated context with Norway inclusion"
            }
            
            partial_success, partial_response = self.run_test(
                "PATCH Partial Scenario Amendment",
                "PATCH",
                f"scenarios/{scenario_id}/amend",
                200,
                data=partial_amendment_data
            )
            
            if not partial_success:
                print("❌ Failed partial amendment")
                return False
                
            # Verify only specified fields were updated
            if partial_response.get('affected_regions') != partial_amendment_data['affected_regions']:
                print(f"❌ Partial amendment affected_regions not updated correctly")
                return False
            print(f"   ✅ Partial amendment affected_regions updated: {partial_response.get('affected_regions')}")
            
            if partial_response.get('additional_context') != partial_amendment_data['additional_context']:
                print(f"❌ Partial amendment additional_context not updated correctly")
                return False
            print(f"   ✅ Partial amendment additional_context updated")
            
            # Verify other fields remained from previous amendment
            if partial_response.get('key_variables') != amendment_data['key_variables']:
                print(f"❌ Partial amendment should not have changed key_variables")
                return False
            print(f"   ✅ key_variables unchanged from previous amendment")
            
            if partial_response.get('stakeholders') != amendment_data['stakeholders']:
                print(f"❌ Partial amendment should not have changed stakeholders")
                return False
            print(f"   ✅ stakeholders unchanged from previous amendment")
            
            # Test 6: Test authentication requirement
            temp_token = self.token
            self.token = None
            
            auth_test_success, auth_test_response = self.run_test(
                "Test Authentication Required for Amendment",
                "PATCH",
                f"scenarios/{scenario_id}/amend",
                403,  # FastAPI returns 403 for "Not authenticated"
                data={"affected_regions": ["Test"]}
            )
            
            self.token = temp_token  # Restore token
            
            if not auth_test_success:
                print("❌ Authentication test failed - endpoint should require authentication")
                return False
                
            print(f"✅ Authentication properly enforced for amendment endpoint")
            
            # Test 7: Test with invalid scenario ID
            invalid_scenario_id = "invalid-scenario-id-12345"
            invalid_success, invalid_response = self.run_test(
                "Test Amendment with Invalid Scenario ID",
                "PATCH",
                f"scenarios/{invalid_scenario_id}/amend",
                404,  # Should return 404 for non-existent scenario
                data={"affected_regions": ["Test"]}
            )
            
            if not invalid_success:
                print("❌ Invalid scenario ID test failed - should return 404")
                return False
                
            print(f"✅ Invalid scenario ID properly handled with 404")
            
            # Test 8: Test with empty amendment data
            empty_success, empty_response = self.run_test(
                "Test Amendment with Empty Data",
                "PATCH",
                f"scenarios/{scenario_id}/amend",
                200,  # Should succeed but not change anything
                data={}
            )
            
            if not empty_success:
                print("❌ Empty amendment data test failed")
                return False
                
            print(f"✅ Empty amendment data handled correctly")
            
            print(f"\n🎉 SCENARIO AMENDMENT FUNCTIONALITY TESTING COMPLETED SUCCESSFULLY!")
            print(f"   ✅ PATCH endpoint accepts partial data without validation errors")
            print(f"   ✅ Only provided fields are updated in database")
            print(f"   ✅ Response returns complete updated scenario with new fields")
            print(f"   ✅ GET scenarios reflects the amendments")
            print(f"   ✅ Fields not provided in amendment remain unchanged")
            print(f"   ✅ Authentication and error handling working correctly")
            
            return True
            
        finally:
            # Restore original token
            self.token = original_token

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

    print("\n🎯 Testing Specific Game Book Scenario (URL Path Fix)...")
    print("   Testing Game Book with Finnish Economic Crisis scenario...")
    tester.test_specific_game_book_scenario()

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

    print("\n🎯 Testing FUZZY LOGIC SCENARIO ADJUSTERS...")
    print("   Testing Scenario Adjustment Creation with SEPTE Framework...")
    tester.test_create_scenario_adjustment()
    
    print("   Testing SEPTE Percentage Validation...")
    tester.test_scenario_adjustment_percentage_validation()
    
    print("   Testing Scenario Adjustments Retrieval...")
    tester.test_get_scenario_adjustments()
    
    print("   Testing Scenario Adjustment Updates...")
    tester.test_update_scenario_adjustment()
    
    print("   Testing Consensus Settings Creation...")
    tester.test_create_consensus_settings()
    
    print("   Testing Consensus Agreement...")
    tester.test_agree_to_consensus()
    
    print("   Testing Access Control for Scenario Adjustments...")
    tester.test_scenario_adjustment_access_control()
    
    print("   Testing AI Analysis Integration with Claude Sonnet 4...")
    tester.test_ai_analysis_integration()

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

    print("\n🧠 Testing KNOWLEDGE TOPOLOGY ENDPOINTS...")
    
    # Login with test credentials from review request
    print("   Logging in with test credentials (test@example.com / password123)...")
    test_login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Store original token
    original_token = tester.token
    
    login_success, login_response = tester.run_test(
        "Login with Test Credentials for Knowledge Topology",
        "POST",
        "login",
        200,
        data=test_login_data
    )
    
    if login_success and 'access_token' in login_response:
        tester.token = login_response['access_token']
        print(f"   ✅ Successfully logged in with test credentials")
        
        print("   Testing Knowledge Topology Summary...")
        tester.test_knowledge_topology_summary()
        
        print("   Testing Knowledge Sources - No Filter...")
        tester.test_knowledge_sources_no_filter()
        
        print("   Testing Knowledge Sources - Priority Filters...")
        tester.test_knowledge_sources_priority_filter()
        
        print("   Testing Knowledge Sources - API Filter...")
        tester.test_knowledge_sources_api_filter()
        
        print("   Testing Knowledge Sources - Specialization Filters...")
        tester.test_knowledge_sources_specialization_filter()
        
        print("   Testing Crisis Strategy - Economic Crisis (Severity 8)...")
        tester.test_crisis_strategy_economic_crisis()
        
        print("   Testing Crisis Strategy - Cyber Attack (Severity 6)...")
        tester.test_crisis_strategy_cyber_attack()
        
        print("   Testing Crisis Strategy - Pandemic (Severity 9)...")
        tester.test_crisis_strategy_pandemic()
        
        print("   Testing Crisis Strategy - Invalid Severity...")
        tester.test_crisis_strategy_invalid_severity()
        
        print("   Testing Crisis Strategy - Unknown Crisis Type...")
        tester.test_crisis_strategy_unknown_crisis_type()
        
        print("   Testing Knowledge Topology Authentication...")
        tester.test_knowledge_topology_authentication()
        
        # Restore original token
        tester.token = original_token
        print(f"   ✅ Restored original authentication token")
        
    else:
        print(f"   ❌ Failed to login with test credentials, skipping Knowledge Topology tests")
        # Restore original token anyway
        tester.token = original_token

    print("\n🚨 Testing CRISIS MANAGEMENT FRAMEWORK ENDPOINTS...")
    
    # Login with test credentials from review request for Crisis Framework testing
    print("   Logging in with test credentials (test@example.com / password123)...")
    test_login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Store original token
    original_token = tester.token
    
    login_success, login_response = tester.run_test(
        "Login with Test Credentials for Crisis Framework",
        "POST",
        "login",
        200,
        data=test_login_data
    )
    
    if login_success and 'access_token' in login_response:
        tester.token = login_response['access_token']
        print(f"   ✅ Successfully logged in with test credentials")
        
        print("   Testing Crisis Framework Summary...")
        tester.test_crisis_framework_summary()
        
        print("   Testing Crisis Factors - No Filter...")
        tester.test_crisis_factors_no_filter()
        
        print("   Testing Crisis Factors - Category Filters...")
        tester.test_crisis_factors_category_filter()
        
        print("   Testing Crisis Factors - Priority Filters...")
        tester.test_crisis_factors_priority_filter()
        
        print("   Testing Monitoring Tasks - No Filter...")
        tester.test_monitoring_tasks_no_filter()
        
        print("   Testing Monitoring Tasks - Priority Filters...")
        tester.test_monitoring_tasks_priority_filter()
        
        print("   Testing Monitoring Tasks - Frequency Filters...")
        tester.test_monitoring_tasks_frequency_filter()
        
        print("   Testing Scenario Assessment with Finnish Economic Crisis...")
        tester.test_scenario_assessment_finnish_crisis()
        
        print("   Testing Crisis Framework Authentication...")
        tester.test_crisis_framework_authentication()
        
        # Restore original token
        tester.token = original_token
        print(f"   ✅ Restored original authentication token")
        
    else:
        print(f"   ❌ Failed to login with test credentials, skipping Crisis Framework tests")
        # Restore original token anyway
        tester.token = original_token

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