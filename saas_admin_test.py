import requests
import sys
import json
from datetime import datetime

class SaaSAdminTester:
    def __init__(self, base_url="https://polycrisis-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.client_id = None
        self.avatar_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        elif self.token:
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=60)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=60)

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

    def test_admin_initialize(self):
        """Test Admin System Initialization"""
        success, response = self.run_test(
            "Admin System Initialize",
            "POST",
            "admin/initialize",
            200
        )
        
        if success:
            print(f"   Admin initialized for: rauno.saarnio@xr-presence.com")
            return True
        return False

    def test_admin_registration(self):
        """Test Admin User Registration"""
        # Try with a different admin email first
        admin_user_data = {
            "email": f"admin_{datetime.now().strftime('%H%M%S')}@xr-presence.com",
            "username": f"admin_{datetime.now().strftime('%H%M%S')}",
            "password": "AdminPass123!",
            "organization": "XR Presence Admin",
            "job_title": "Super Admin",
            "department": "Administration"
        }
        
        success, response = self.run_test(
            "Admin User Registration (New Admin)",
            "POST",
            "register",
            200,
            data=admin_user_data
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_email = admin_user_data['email']
            print(f"   Admin token received: {self.admin_token[:20]}...")
            
            # Now initialize this new user as admin
            admin_init_data = {
                "admin_email": self.admin_email,
                "admin_level": "super_admin",
                "permissions": ["all"]
            }
            
            init_success, init_response = self.run_test(
                "Initialize New Admin",
                "POST",
                "admin/initialize-user",
                200,
                data=admin_init_data
            )
            
            return True
        return False

    def test_admin_login(self):
        """Test Admin User Login"""
        login_data = {
            "email": "rauno.saarnio@xr-presence.com",
            "password": "AdminPass123!"
        }
        
        success, response = self.run_test(
            "Admin User Login",
            "POST",
            "login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin login token: {self.admin_token[:20]}...")
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
            return True, response
        return False, []

    def test_create_client(self):
        """Test Client Management - Create Client"""
        # First get license tiers to use one
        tier_success, tier_response = self.test_get_license_tiers()
        
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
            
            # Store first avatar ID for testing
            if response:
                self.avatar_id = response[0]['id']
            return True, response
        return False, []

    def test_update_avatar_status(self):
        """Test AI Avatar Status Management"""
        if not self.avatar_id:
            # Try to get avatars first
            avatar_success, avatar_response = self.test_get_ai_avatars()
            if not avatar_success or not avatar_response:
                print("❌ Could not get avatars for status update")
                return False
            
        # Test different status updates
        statuses = ["active", "monitoring", "learning", "inactive"]
        successful_updates = 0
        
        for status in statuses:
            status_data = {"status": status}
            
            success, response = self.run_test(
                f"Update Avatar Status to {status}",
                "PUT",
                f"admin/ai-avatars/{self.avatar_id}/status",
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
        if not self.avatar_id:
            # Try to get avatars first
            avatar_success, avatar_response = self.test_get_ai_avatars()
            if not avatar_success or not avatar_response:
                print("❌ Could not get avatars for competence addition")
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
            f"avatars/{self.avatar_id}/competences",
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
        if not self.avatar_id:
            print("❌ No avatar ID available for competence retrieval")
            return False
            
        success, response = self.run_test(
            "Get Avatar Competences",
            "GET",
            f"avatars/{self.avatar_id}/competences",
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
        if not self.client_id:
            print("❌ No client ID available for payment intent creation")
            return False
            
        # Get license tiers first
        tier_success, tier_response = self.test_get_license_tiers()
        if not tier_success or not tier_response:
            print("❌ Could not get license tiers for payment")
            return False
            
        license_tier_id = tier_response[0]['id'] if tier_response else None
        
        payment_data = {
            "client_id": self.client_id,
            "license_tier_id": license_tier_id,
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

def main():
    print("🚀 Starting SaaS Admin Platform API Tests")
    print("=" * 50)
    
    tester = SaaSAdminTester()
    
    # Test sequence for SaaS Admin Platform
    print("\n👑 Testing SaaS Admin Platform Setup...")
    
    # Initialize admin system
    if not tester.test_admin_initialize():
        print("❌ Admin initialization failed")
        
    # Try to login as admin (if already exists)
    admin_login_success = tester.test_admin_login()
    
    # If login failed, try to register admin
    if not admin_login_success:
        print("   Admin login failed, trying registration...")
        if not tester.test_admin_registration():
            print("❌ Admin registration failed, stopping tests")
            return 1
    
    print("\n📋 Testing License Tier Management...")
    tester.test_get_license_tiers()
    
    print("\n👥 Testing Client Management System...")
    tester.test_create_client()
    tester.test_get_clients()
    
    print("\n🤖 Testing AI Avatar Management...")
    tester.test_get_ai_avatars()
    tester.test_update_avatar_status()
    
    print("\n🧠 Testing Avatar Competence Management...")
    tester.test_add_avatar_competence()
    tester.test_get_avatar_competences()
    
    print("\n💳 Testing Stripe Payment Integration...")
    tester.test_create_stripe_payment_intent()
    
    print("\n📊 Testing Admin Dashboard Analytics...")
    tester.test_admin_dashboard_stats()

    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All SaaS Admin tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())