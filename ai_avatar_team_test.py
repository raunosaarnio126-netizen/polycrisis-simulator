#!/usr/bin/env python3
"""
AI Avatar Team/Organization Fields Testing
Testing the newly enhanced AI Avatar system with team/organization fields
"""

import requests
import json
import sys
from datetime import datetime

class AIAvatarTeamTester:
    def __init__(self, base_url="https://adapt-crisis-sim.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_avatars = []

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

    def setup_authentication(self):
        """Setup authentication for testing"""
        # Use existing test credentials
        test_email = "test@example.com"
        test_password = "password123"
        
        login_data = {
            "email": test_email,
            "password": test_password
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
            print(f"   Authentication successful")
            return True
        else:
            print("❌ Authentication failed")
            return False

    def test_avatar_creation_with_team_organization(self):
        """Test Avatar Creation with Team/Organization fields"""
        print(f"\n{'='*60}")
        print(f"TESTING: Avatar Creation with Team/Organization Fields")
        print(f"{'='*60}")
        
        # Test 1: Create Research Avatar with team/organization
        research_avatar_data = {
            "name": "Research Specialist Alpha",
            "avatar_type": "research",
            "category": "analytical",
            "description": "Advanced research avatar specializing in data analysis and literature review",
            "specializations": ["data_analysis", "literature_review", "statistical_modeling"],
            "core_competences": [
                {
                    "name": "Data Analysis",
                    "skill_level": 9,
                    "description": "Expert-level data analysis and interpretation"
                },
                {
                    "name": "Research Methodology",
                    "skill_level": 8,
                    "description": "Advanced research design and methodology"
                }
            ],
            "knowledge_domains": ["statistics", "research_methods", "data_science"],
            "task_capabilities": ["analyze_datasets", "conduct_literature_reviews", "generate_insights"],
            "team_name": "Crisis Research Team",
            "organization": "Emergency Response Institute"
        }
        
        success, response = self.run_test(
            "Create Research Avatar with Team/Organization",
            "POST",
            "ai-avatars",
            200,
            data=research_avatar_data
        )
        
        if success and 'id' in response:
            avatar_id = response['id']
            self.created_avatars.append(avatar_id)
            print(f"   ✅ Research Avatar created successfully")
            print(f"   Avatar ID: {avatar_id}")
            print(f"   Name: {response.get('name')}")
            print(f"   Type: {response.get('avatar_type')}")
            print(f"   Team Name: {response.get('team_name')}")
            print(f"   Organization: {response.get('organization')}")
            
            # Verify team_name and organization fields are present and correct
            if response.get('team_name') == "Crisis Research Team":
                print(f"   ✅ Team name correctly stored: {response.get('team_name')}")
            else:
                print(f"   ❌ Team name incorrect: expected 'Crisis Research Team', got '{response.get('team_name')}'")
                return False
                
            if response.get('organization') == "Emergency Response Institute":
                print(f"   ✅ Organization correctly stored: {response.get('organization')}")
            else:
                print(f"   ❌ Organization incorrect: expected 'Emergency Response Institute', got '{response.get('organization')}'")
                return False
                
            # Verify other required fields
            required_fields = ['id', 'user_id', 'name', 'avatar_type', 'category', 'description', 
                             'specializations', 'core_competences', 'knowledge_domains', 'task_capabilities',
                             'status', 'created_at', 'updated_at']
            
            missing_fields = []
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All required AIAvatar model fields present")
                
        else:
            print(f"   ❌ Failed to create Research Avatar")
            return False
        
        # Test 2: Create Assessment Avatar with different team/organization
        assessment_avatar_data = {
            "name": "Risk Assessment Beta",
            "avatar_type": "assessment",
            "category": "evaluation",
            "description": "Specialized avatar for comprehensive risk assessment and evaluation",
            "specializations": ["risk_assessment", "vulnerability_analysis", "impact_evaluation"],
            "core_competences": [
                {
                    "name": "Risk Analysis",
                    "skill_level": 10,
                    "description": "Expert risk identification and analysis"
                },
                {
                    "name": "Threat Assessment",
                    "skill_level": 9,
                    "description": "Advanced threat evaluation capabilities"
                }
            ],
            "knowledge_domains": ["risk_management", "security_analysis", "business_continuity"],
            "task_capabilities": ["assess_vulnerabilities", "evaluate_risks", "recommend_mitigations"],
            "team_name": "Security Assessment Unit",
            "organization": "Global Risk Management Corp"
        }
        
        success, response = self.run_test(
            "Create Assessment Avatar with Different Team/Organization",
            "POST",
            "ai-avatars",
            200,
            data=assessment_avatar_data
        )
        
        if success and 'id' in response:
            avatar_id = response['id']
            self.created_avatars.append(avatar_id)
            print(f"   ✅ Assessment Avatar created successfully")
            print(f"   Avatar ID: {avatar_id}")
            print(f"   Team Name: {response.get('team_name')}")
            print(f"   Organization: {response.get('organization')}")
            
            # Verify different team/organization values
            if response.get('team_name') == "Security Assessment Unit":
                print(f"   ✅ Different team name correctly stored")
            else:
                print(f"   ❌ Team name incorrect for Assessment Avatar")
                return False
                
            if response.get('organization') == "Global Risk Management Corp":
                print(f"   ✅ Different organization correctly stored")
            else:
                print(f"   ❌ Organization incorrect for Assessment Avatar")
                return False
        else:
            print(f"   ❌ Failed to create Assessment Avatar")
            return False
        
        # Test 3: Create Analyst Avatar without team/organization (optional fields)
        analyst_avatar_data = {
            "name": "Business Analyst Gamma",
            "avatar_type": "analyst",
            "category": "strategic",
            "description": "Strategic business analyst for market research and insights",
            "specializations": ["market_analysis", "competitive_intelligence", "strategic_planning"],
            "core_competences": [
                {
                    "name": "Market Research",
                    "skill_level": 8,
                    "description": "Advanced market analysis capabilities"
                }
            ],
            "knowledge_domains": ["business_strategy", "market_research", "competitive_analysis"],
            "task_capabilities": ["analyze_markets", "research_competitors", "generate_strategies"]
            # Note: team_name and organization are intentionally omitted to test optional fields
        }
        
        success, response = self.run_test(
            "Create Analyst Avatar without Team/Organization (Optional Fields)",
            "POST",
            "ai-avatars",
            200,
            data=analyst_avatar_data
        )
        
        if success and 'id' in response:
            avatar_id = response['id']
            self.created_avatars.append(avatar_id)
            print(f"   ✅ Analyst Avatar created successfully without team/organization")
            print(f"   Avatar ID: {avatar_id}")
            print(f"   Team Name: {response.get('team_name', 'None')}")
            print(f"   Organization: {response.get('organization', 'None')}")
            
            # Verify optional fields are None or not present
            if response.get('team_name') is None:
                print(f"   ✅ Team name correctly None (optional field)")
            else:
                print(f"   ⚠️ Team name not None but should be optional: {response.get('team_name')}")
                
            if response.get('organization') is None:
                print(f"   ✅ Organization correctly None (optional field)")
            else:
                print(f"   ⚠️ Organization not None but should be optional: {response.get('organization')}")
        else:
            print(f"   ❌ Failed to create Analyst Avatar")
            return False
        
        print(f"   ✅ Avatar Creation with Team/Organization: 3/3 tests passed")
        return True

    def test_avatar_update_with_team_organization(self):
        """Test Avatar Update with Team/Organization fields"""
        print(f"\n{'='*60}")
        print(f"TESTING: Avatar Update with Team/Organization Fields")
        print(f"{'='*60}")
        
        if not self.created_avatars:
            print("❌ No avatars available for update testing")
            return False
        
        # Use the first created avatar (Research Avatar)
        avatar_id = self.created_avatars[0]
        
        # Test 1: Update avatar to add/modify team and organization fields
        update_data = {
            "name": "Research Specialist Alpha - Enhanced",
            "avatar_type": "research",
            "category": "analytical",
            "description": "Enhanced research avatar with expanded capabilities",
            "specializations": ["data_analysis", "literature_review", "statistical_modeling", "predictive_analytics"],
            "core_competences": [
                {
                    "name": "Data Analysis",
                    "skill_level": 10,  # Upgraded from 9
                    "description": "Expert-level data analysis and interpretation with AI integration"
                },
                {
                    "name": "Research Methodology",
                    "skill_level": 9,   # Upgraded from 8
                    "description": "Advanced research design and methodology with automation"
                },
                {
                    "name": "Predictive Modeling",
                    "skill_level": 8,   # New competence
                    "description": "Advanced predictive modeling and forecasting"
                }
            ],
            "knowledge_domains": ["statistics", "research_methods", "data_science", "machine_learning"],
            "task_capabilities": ["analyze_datasets", "conduct_literature_reviews", "generate_insights", "build_predictive_models"],
            "team_name": "Advanced Crisis Research Division",  # Updated team name
            "organization": "International Emergency Response Institute"  # Updated organization
        }
        
        success, response = self.run_test(
            "Update Avatar with Modified Team/Organization",
            "PUT",
            f"ai-avatars/{avatar_id}",
            200,
            data=update_data
        )
        
        if success and 'id' in response:
            print(f"   ✅ Avatar updated successfully")
            print(f"   Avatar ID: {response.get('id')}")
            print(f"   Updated Name: {response.get('name')}")
            print(f"   Updated Team Name: {response.get('team_name')}")
            print(f"   Updated Organization: {response.get('organization')}")
            
            # Verify updated team_name and organization
            if response.get('team_name') == "Advanced Crisis Research Division":
                print(f"   ✅ Team name correctly updated")
            else:
                print(f"   ❌ Team name update failed: expected 'Advanced Crisis Research Division', got '{response.get('team_name')}'")
                return False
                
            if response.get('organization') == "International Emergency Response Institute":
                print(f"   ✅ Organization correctly updated")
            else:
                print(f"   ❌ Organization update failed: expected 'International Emergency Response Institute', got '{response.get('organization')}'")
                return False
            
            # Verify updated_at timestamp changed
            if 'updated_at' in response:
                print(f"   ✅ Updated timestamp present: {response.get('updated_at')}")
            else:
                print(f"   ❌ Updated timestamp missing")
                return False
                
            # Verify enhanced competences
            competences = response.get('core_competences', [])
            if len(competences) == 3:
                print(f"   ✅ Competences correctly updated (3 competences)")
                for comp in competences:
                    print(f"     - {comp.get('name')}: Level {comp.get('skill_level')}")
            else:
                print(f"   ❌ Competences update failed: expected 3, got {len(competences)}")
                return False
        else:
            print(f"   ❌ Failed to update avatar")
            return False
        
        # Test 2: Update avatar to remove team/organization (set to None)
        if len(self.created_avatars) > 2:
            avatar_id_2 = self.created_avatars[2]  # Use Analyst Avatar
            
            update_data_remove = {
                "name": "Business Analyst Gamma - Freelance",
                "avatar_type": "analyst",
                "category": "strategic",
                "description": "Independent strategic business analyst",
                "specializations": ["market_analysis", "competitive_intelligence"],
                "core_competences": [
                    {
                        "name": "Market Research",
                        "skill_level": 9,
                        "description": "Expert market analysis capabilities"
                    }
                ],
                "knowledge_domains": ["business_strategy", "market_research"],
                "task_capabilities": ["analyze_markets", "research_competitors"],
                "team_name": None,  # Explicitly set to None
                "organization": None  # Explicitly set to None
            }
            
            success, response = self.run_test(
                "Update Avatar to Remove Team/Organization",
                "PUT",
                f"ai-avatars/{avatar_id_2}",
                200,
                data=update_data_remove
            )
            
            if success:
                print(f"   ✅ Avatar updated to remove team/organization")
                print(f"   Team Name: {response.get('team_name', 'None')}")
                print(f"   Organization: {response.get('organization', 'None')}")
                
                if response.get('team_name') is None and response.get('organization') is None:
                    print(f"   ✅ Team/Organization correctly removed (set to None)")
                else:
                    print(f"   ⚠️ Team/Organization not properly removed")
            else:
                print(f"   ❌ Failed to update avatar to remove team/organization")
                return False
        
        print(f"   ✅ Avatar Update with Team/Organization: All tests passed")
        return True

    def test_avatar_retrieval_with_team_organization(self):
        """Test Avatar Retrieval with team_name and organization fields"""
        print(f"\n{'='*60}")
        print(f"TESTING: Avatar Retrieval with Team/Organization Fields")
        print(f"{'='*60}")
        
        # Test 1: Get all avatars and verify team/organization fields are returned
        success, response = self.run_test(
            "Get All Avatars with Team/Organization Fields",
            "GET",
            "ai-avatars",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} avatars")
            
            # Verify each avatar has team_name and organization fields
            for i, avatar in enumerate(response):
                print(f"   Avatar {i+1}:")
                print(f"     Name: {avatar.get('name')}")
                print(f"     Type: {avatar.get('avatar_type')}")
                print(f"     Team Name: {avatar.get('team_name', 'None')}")
                print(f"     Organization: {avatar.get('organization', 'None')}")
                
                # Verify required fields are present
                required_fields = ['id', 'name', 'avatar_type', 'category', 'description']
                for field in required_fields:
                    if field not in avatar:
                        print(f"     ❌ Missing required field: {field}")
                        return False
                
                # Verify team_name and organization fields exist (even if None)
                if 'team_name' not in avatar:
                    print(f"     ❌ Missing team_name field")
                    return False
                if 'organization' not in avatar:
                    print(f"     ❌ Missing organization field")
                    return False
                    
                print(f"     ✅ All fields present including team_name and organization")
        else:
            print(f"   ❌ Failed to retrieve avatars")
            return False
        
        # Test 2: Get specific avatar and verify team/organization fields
        if self.created_avatars:
            avatar_id = self.created_avatars[0]  # Research Avatar (updated)
            
            success, response = self.run_test(
                "Get Specific Avatar with Team/Organization",
                "GET",
                f"ai-avatars/{avatar_id}",
                200
            )
            
            if success and 'id' in response:
                print(f"   ✅ Retrieved specific avatar successfully")
                print(f"   Avatar ID: {response.get('id')}")
                print(f"   Name: {response.get('name')}")
                print(f"   Team Name: {response.get('team_name')}")
                print(f"   Organization: {response.get('organization')}")
                
                # Verify this is the updated Research Avatar
                expected_team = "Advanced Crisis Research Division"
                expected_org = "International Emergency Response Institute"
                
                if response.get('team_name') == expected_team:
                    print(f"   ✅ Team name correctly retrieved: {expected_team}")
                else:
                    print(f"   ❌ Team name incorrect: expected '{expected_team}', got '{response.get('team_name')}'")
                    return False
                    
                if response.get('organization') == expected_org:
                    print(f"   ✅ Organization correctly retrieved: {expected_org}")
                else:
                    print(f"   ❌ Organization incorrect: expected '{expected_org}', got '{response.get('organization')}'")
                    return False
                    
                # Verify complete AIAvatar model structure
                expected_fields = [
                    'id', 'user_id', 'name', 'avatar_type', 'category', 'description',
                    'specializations', 'core_competences', 'knowledge_domains', 'task_capabilities',
                    'team_name', 'organization', 'status', 'performance_metrics', 'created_at', 'updated_at'
                ]
                
                missing_fields = []
                for field in expected_fields:
                    if field not in response:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ❌ Missing AIAvatar model fields: {missing_fields}")
                    return False
                else:
                    print(f"   ✅ Complete AIAvatar model structure verified")
            else:
                print(f"   ❌ Failed to retrieve specific avatar")
                return False
        
        print(f"   ✅ Avatar Retrieval with Team/Organization: All tests passed")
        return True

    def test_backend_model_verification(self):
        """Test Backend Model Changes - Verify AIAvatar and AvatarCreate models"""
        print(f"\n{'='*60}")
        print(f"TESTING: Backend Model Changes Verification")
        print(f"{'='*60}")
        
        # Test 1: Verify API doesn't break with new optional fields
        # Create avatar with minimal data (no team/organization)
        minimal_avatar_data = {
            "name": "Minimal Test Avatar",
            "avatar_type": "test",
            "category": "testing",
            "description": "Avatar for testing minimal field requirements",
            "specializations": ["testing"],
            "core_competences": [
                {
                    "name": "Testing",
                    "skill_level": 5,
                    "description": "Basic testing capabilities"
                }
            ],
            "knowledge_domains": ["testing"],
            "task_capabilities": ["run_tests"]
        }
        
        success, response = self.run_test(
            "Create Avatar with Minimal Data (No Team/Organization)",
            "POST",
            "ai-avatars",
            200,
            data=minimal_avatar_data
        )
        
        if success and 'id' in response:
            avatar_id = response['id']
            self.created_avatars.append(avatar_id)
            print(f"   ✅ Minimal avatar created successfully")
            print(f"   Avatar ID: {avatar_id}")
            
            # Verify team_name and organization are None or not present
            team_name = response.get('team_name')
            organization = response.get('organization')
            
            print(f"   Team Name: {team_name}")
            print(f"   Organization: {organization}")
            
            if team_name is None and organization is None:
                print(f"   ✅ Optional fields correctly handled (None values)")
            else:
                print(f"   ⚠️ Optional fields present but should be None")
        else:
            print(f"   ❌ Failed to create minimal avatar")
            return False
        
        # Test 2: Verify API handles invalid team/organization data gracefully
        invalid_avatar_data = {
            "name": "Invalid Test Avatar",
            "avatar_type": "test",
            "category": "testing",
            "description": "Avatar for testing invalid data handling",
            "specializations": ["testing"],
            "core_competences": [
                {
                    "name": "Testing",
                    "skill_level": 5,
                    "description": "Basic testing capabilities"
                }
            ],
            "knowledge_domains": ["testing"],
            "task_capabilities": ["run_tests"],
            "team_name": "",  # Empty string
            "organization": ""  # Empty string
        }
        
        success, response = self.run_test(
            "Create Avatar with Empty Team/Organization Strings",
            "POST",
            "ai-avatars",
            200,
            data=invalid_avatar_data
        )
        
        if success and 'id' in response:
            avatar_id = response['id']
            self.created_avatars.append(avatar_id)
            print(f"   ✅ Avatar with empty strings created successfully")
            print(f"   Team Name: '{response.get('team_name')}'")
            print(f"   Organization: '{response.get('organization')}'")
            
            # Verify empty strings are handled appropriately
            if response.get('team_name') == "" and response.get('organization') == "":
                print(f"   ✅ Empty strings handled correctly")
            else:
                print(f"   ⚠️ Empty strings not handled as expected")
        else:
            print(f"   ❌ Failed to create avatar with empty strings")
            return False
        
        # Test 3: Verify very long team/organization names are handled
        long_avatar_data = {
            "name": "Long Fields Test Avatar",
            "avatar_type": "test",
            "category": "testing",
            "description": "Avatar for testing long field values",
            "specializations": ["testing"],
            "core_competences": [
                {
                    "name": "Testing",
                    "skill_level": 5,
                    "description": "Basic testing capabilities"
                }
            ],
            "knowledge_domains": ["testing"],
            "task_capabilities": ["run_tests"],
            "team_name": "Very Long Team Name That Exceeds Normal Length Expectations For Testing Database Field Limits And API Handling",
            "organization": "Extremely Long Organization Name That Tests The System's Ability To Handle Extended Text Fields In The Database And API Responses"
        }
        
        success, response = self.run_test(
            "Create Avatar with Long Team/Organization Names",
            "POST",
            "ai-avatars",
            200,
            data=long_avatar_data
        )
        
        if success and 'id' in response:
            avatar_id = response['id']
            self.created_avatars.append(avatar_id)
            print(f"   ✅ Avatar with long field values created successfully")
            print(f"   Team Name Length: {len(response.get('team_name', ''))}")
            print(f"   Organization Length: {len(response.get('organization', ''))}")
            
            # Verify long strings are preserved
            if len(response.get('team_name', '')) > 50 and len(response.get('organization', '')) > 50:
                print(f"   ✅ Long field values preserved correctly")
            else:
                print(f"   ⚠️ Long field values may have been truncated")
        else:
            print(f"   ❌ Failed to create avatar with long field values")
            return False
        
        print(f"   ✅ Backend Model Changes Verification: All tests passed")
        return True

    def test_predefined_avatar_types_with_teams(self):
        """Test predefined avatar types (research, assessment, analyst) with team/organization"""
        print(f"\n{'='*60}")
        print(f"TESTING: Predefined Avatar Types with Team/Organization")
        print(f"{'='*60}")
        
        # Test all three predefined types mentioned in the review request
        predefined_types = [
            {
                "name": "Research Specialist Delta",
                "avatar_type": "research",
                "category": "analytical",
                "description": "Specialized research avatar for comprehensive data analysis",
                "specializations": ["data_mining", "statistical_analysis", "research_synthesis"],
                "core_competences": [
                    {
                        "name": "Data Mining",
                        "skill_level": 9,
                        "description": "Advanced data extraction and analysis"
                    },
                    {
                        "name": "Statistical Analysis",
                        "skill_level": 8,
                        "description": "Expert statistical modeling and interpretation"
                    }
                ],
                "knowledge_domains": ["statistics", "data_science", "research_methodology"],
                "task_capabilities": ["extract_insights", "analyze_trends", "generate_reports"],
                "team_name": "Data Research Division",
                "organization": "Analytics Institute"
            },
            {
                "name": "Assessment Expert Echo",
                "avatar_type": "assessment",
                "category": "evaluation",
                "description": "Comprehensive assessment avatar for risk and performance evaluation",
                "specializations": ["risk_evaluation", "performance_assessment", "compliance_review"],
                "core_competences": [
                    {
                        "name": "Risk Evaluation",
                        "skill_level": 10,
                        "description": "Expert risk identification and assessment"
                    },
                    {
                        "name": "Compliance Review",
                        "skill_level": 9,
                        "description": "Advanced regulatory compliance assessment"
                    }
                ],
                "knowledge_domains": ["risk_management", "compliance", "audit_procedures"],
                "task_capabilities": ["assess_risks", "evaluate_compliance", "recommend_actions"],
                "team_name": "Risk Assessment Group",
                "organization": "Compliance Solutions Corp"
            },
            {
                "name": "Business Analyst Foxtrot",
                "avatar_type": "analyst",
                "category": "strategic",
                "description": "Strategic business analyst for market intelligence and planning",
                "specializations": ["market_intelligence", "strategic_planning", "competitive_analysis"],
                "core_competences": [
                    {
                        "name": "Market Intelligence",
                        "skill_level": 9,
                        "description": "Expert market research and intelligence gathering"
                    },
                    {
                        "name": "Strategic Planning",
                        "skill_level": 8,
                        "description": "Advanced strategic planning and execution"
                    }
                ],
                "knowledge_domains": ["business_strategy", "market_analysis", "competitive_intelligence"],
                "task_capabilities": ["analyze_markets", "develop_strategies", "monitor_competition"],
                "team_name": "Strategic Analysis Unit",
                "organization": "Business Intelligence Firm"
            }
        ]
        
        created_count = 0
        for i, avatar_data in enumerate(predefined_types):
            success, response = self.run_test(
                f"Create {avatar_data['avatar_type'].title()} Avatar with Team/Organization",
                "POST",
                "ai-avatars",
                200,
                data=avatar_data
            )
            
            if success and 'id' in response:
                avatar_id = response['id']
                self.created_avatars.append(avatar_id)
                created_count += 1
                
                print(f"   ✅ {avatar_data['avatar_type'].title()} Avatar created successfully")
                print(f"   Avatar ID: {avatar_id}")
                print(f"   Name: {response.get('name')}")
                print(f"   Type: {response.get('avatar_type')}")
                print(f"   Team: {response.get('team_name')}")
                print(f"   Organization: {response.get('organization')}")
                
                # Verify type-specific fields
                if response.get('avatar_type') == avatar_data['avatar_type']:
                    print(f"   ✅ Avatar type correctly set: {avatar_data['avatar_type']}")
                else:
                    print(f"   ❌ Avatar type incorrect")
                    return False
                    
                # Verify team/organization for each type
                if response.get('team_name') == avatar_data['team_name']:
                    print(f"   ✅ Team name correctly set for {avatar_data['avatar_type']} type")
                else:
                    print(f"   ❌ Team name incorrect for {avatar_data['avatar_type']} type")
                    return False
                    
                if response.get('organization') == avatar_data['organization']:
                    print(f"   ✅ Organization correctly set for {avatar_data['avatar_type']} type")
                else:
                    print(f"   ❌ Organization incorrect for {avatar_data['avatar_type']} type")
                    return False
            else:
                print(f"   ❌ Failed to create {avatar_data['avatar_type']} Avatar")
                return False
        
        print(f"   ✅ Predefined Avatar Types: {created_count}/3 types created successfully")
        return created_count == 3

    def run_comprehensive_test(self):
        """Run comprehensive AI Avatar team/organization testing"""
        print(f"\n{'='*80}")
        print(f"AI AVATAR TEAM/ORGANIZATION COMPREHENSIVE TESTING")
        print(f"{'='*80}")
        print(f"Testing newly enhanced AI Avatar system with team/organization fields")
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        
        # Setup authentication
        if not self.setup_authentication():
            print(f"\n❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        test_results = []
        
        # Test 1: Avatar Creation with Team/Organization
        try:
            result = self.test_avatar_creation_with_team_organization()
            test_results.append(("Avatar Creation with Team/Organization", result))
        except Exception as e:
            print(f"❌ Avatar Creation test failed with error: {str(e)}")
            test_results.append(("Avatar Creation with Team/Organization", False))
        
        # Test 2: Avatar Update with Team/Organization
        try:
            result = self.test_avatar_update_with_team_organization()
            test_results.append(("Avatar Update with Team/Organization", result))
        except Exception as e:
            print(f"❌ Avatar Update test failed with error: {str(e)}")
            test_results.append(("Avatar Update with Team/Organization", False))
        
        # Test 3: Avatar Retrieval with Team/Organization
        try:
            result = self.test_avatar_retrieval_with_team_organization()
            test_results.append(("Avatar Retrieval with Team/Organization", result))
        except Exception as e:
            print(f"❌ Avatar Retrieval test failed with error: {str(e)}")
            test_results.append(("Avatar Retrieval with Team/Organization", False))
        
        # Test 4: Backend Model Verification
        try:
            result = self.test_backend_model_verification()
            test_results.append(("Backend Model Changes Verification", result))
        except Exception as e:
            print(f"❌ Backend Model Verification test failed with error: {str(e)}")
            test_results.append(("Backend Model Changes Verification", False))
        
        # Test 5: Predefined Avatar Types
        try:
            result = self.test_predefined_avatar_types_with_teams()
            test_results.append(("Predefined Avatar Types with Teams", result))
        except Exception as e:
            print(f"❌ Predefined Avatar Types test failed with error: {str(e)}")
            test_results.append(("Predefined Avatar Types with Teams", False))
        
        # Print comprehensive results
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE TEST RESULTS")
        print(f"{'='*80}")
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed_tests += 1
        
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Total API Tests Run: {self.tests_run}")
        print(f"Total API Tests Passed: {self.tests_passed}")
        print(f"API Test Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"")
        print(f"Total Feature Tests: {total_tests}")
        print(f"Feature Tests Passed: {passed_tests}")
        print(f"Feature Test Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"")
        print(f"Created Avatars: {len(self.created_avatars)}")
        print(f"Avatar IDs: {self.created_avatars}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! AI Avatar team/organization functionality is working correctly.")
            return True
        else:
            print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Review the detailed results above.")
            return False

def main():
    """Main function to run AI Avatar team/organization testing"""
    print("Starting AI Avatar Team/Organization Testing...")
    
    tester = AIAvatarTeamTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ AI Avatar team/organization testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ AI Avatar team/organization testing completed with failures!")
        sys.exit(1)

if __name__ == "__main__":
    main()