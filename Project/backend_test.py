import requests
import sys
import json
from datetime import datetime
import uuid

class EmptyClassroomFinderTester:
    def __init__(self, base_url="https://iipsrooms.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@iips.edu.in"
        self.test_user_password = "TestPass123!"
        self.test_user_name = "Test User"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
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
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

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

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        return success

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "name": self.test_user_name,
                "email": self.test_user_email,
                "password": self.test_user_password,
                "role": "student"
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['email']}")
            return True
        return False

    def test_user_login(self):
        """Test user login with registered credentials"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_user_password
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            print(f"   Logged in user: {response['user']['email']}")
            return True
        return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
        )
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        if success:
            print(f"   User info: {response.get('name')} ({response.get('role')})")
        return success

    def test_get_classrooms(self):
        """Test getting all classrooms"""
        success, response = self.run_test(
            "Get All Classrooms",
            "GET",
            "classrooms",
            200
        )
        if success:
            print(f"   Found {len(response)} classrooms")
            # Check if rooms have required fields
            if response:
                room = response[0]
                required_fields = ['room_id', 'floor', 'capacity', 'facilities', 'status', 'predicted_availability']
                missing_fields = [field for field in required_fields if field not in room]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in room data: {missing_fields}")
                else:
                    print(f"   ✅ Room data structure is complete")
        return success

    def test_get_specific_classroom(self):
        """Test getting a specific classroom"""
        success, response = self.run_test(
            "Get Specific Classroom (LT-1)",
            "GET",
            "classrooms/LT-1",
            200
        )
        if success:
            print(f"   Room: {response.get('room_id')} - {response.get('status')}")
        return success

    def test_get_nonexistent_classroom(self):
        """Test getting a non-existent classroom"""
        success, response = self.run_test(
            "Get Non-existent Classroom",
            "GET",
            "classrooms/INVALID-ROOM",
            404
        )
        return success

    def test_natural_language_search_basic(self):
        """Test basic natural language search"""
        success, response = self.run_test(
            "Natural Language Search - Basic",
            "POST",
            "search",
            200,
            data={"query": "show me available rooms"}
        )
        if success:
            if 'rooms' in response and response['rooms']:
                print(f"   Found {len(response['rooms'])} rooms")
            elif 'message' in response:
                print(f"   Message: {response['message']}")
        return success

    def test_natural_language_search_floor_filter(self):
        """Test natural language search with floor filter"""
        success, response = self.run_test(
            "Natural Language Search - Floor Filter",
            "POST",
            "search",
            200,
            data={"query": "rooms on ground floor"}
        )
        if success:
            if 'rooms' in response and response['rooms']:
                ground_floor_rooms = [r for r in response['rooms'] if r['floor'] == 'Ground']
                print(f"   Found {len(ground_floor_rooms)} ground floor rooms")
            elif 'message' in response:
                print(f"   Message: {response['message']}")
        return success

    def test_natural_language_search_facility_filter(self):
        """Test natural language search with facility filter"""
        success, response = self.run_test(
            "Natural Language Search - Facility Filter",
            "POST",
            "search",
            200,
            data={"query": "classrooms with projector"}
        )
        if success:
            if 'rooms' in response and response['rooms']:
                projector_rooms = [r for r in response['rooms'] if 'Projector' in r['facilities']]
                print(f"   Found {len(projector_rooms)} rooms with projector")
            elif 'message' in response:
                print(f"   Message: {response['message']}")
        return success

    def test_natural_language_search_capacity_filter(self):
        """Test natural language search with capacity filter"""
        success, response = self.run_test(
            "Natural Language Search - Capacity Filter",
            "POST",
            "search",
            200,
            data={"query": "rooms for 60 students"}
        )
        if success:
            if 'rooms' in response and response['rooms']:
                large_rooms = [r for r in response['rooms'] if r['capacity'] >= 60]
                print(f"   Found {len(large_rooms)} rooms with 60+ capacity")
            elif 'message' in response:
                print(f"   Message: {response['message']}")
        return success

    def test_natural_language_search_time_validation(self):
        """Test natural language search with invalid time"""
        success, response = self.run_test(
            "Natural Language Search - Time Validation",
            "POST",
            "search",
            200,
            data={"query": "rooms available at 10 PM"}
        )
        if success:
            if 'message' in response and 'valid hours' in response['message'].lower():
                print(f"   ✅ Time validation working: {response['message']}")
            elif 'clarification_needed' in response:
                print(f"   Clarification: {response['clarification_needed']}")
        return success

    def test_natural_language_search_complex(self):
        """Test complex natural language search"""
        success, response = self.run_test(
            "Natural Language Search - Complex Query",
            "POST",
            "search",
            200,
            data={"query": "show me rooms on first floor with projector and speaker for 120 students"}
        )
        if success:
            if 'rooms' in response and response['rooms']:
                print(f"   Found {len(response['rooms'])} matching rooms")
                for room in response['rooms'][:3]:  # Show first 3 rooms
                    print(f"     - {room['room_id']}: {room['capacity']} seats, {room['floor']} floor")
            elif 'message' in response:
                print(f"   Message: {response['message']}")
        return success

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without token"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Unauthorized Access to Classrooms",
            "GET",
            "classrooms",
            401
        )
        
        # Restore token
        self.token = original_token
        return success

    def test_invalid_token_access(self):
        """Test accessing protected endpoints with invalid token"""
        # Temporarily set invalid token
        original_token = self.token
        self.token = "invalid_token_12345"
        
        success, response = self.run_test(
            "Invalid Token Access",
            "GET",
            "classrooms",
            401
        )
        
        # Restore token
        self.token = original_token
        return success

def main():
    print("🚀 Starting Empty Classroom Finder API Tests")
    print("=" * 60)
    
    tester = EmptyClassroomFinderTester()
    
    # Test sequence
    tests = [
        # Basic connectivity
        ("Health Check", tester.test_health_check),
        ("Root Endpoint", tester.test_root_endpoint),
        
        # Authentication tests
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Invalid Login", tester.test_invalid_login),
        ("Get Current User", tester.test_get_current_user),
        
        # Authorization tests
        ("Unauthorized Access", tester.test_unauthorized_access),
        ("Invalid Token Access", tester.test_invalid_token_access),
        
        # Classroom API tests
        ("Get All Classrooms", tester.test_get_classrooms),
        ("Get Specific Classroom", tester.test_get_specific_classroom),
        ("Get Non-existent Classroom", tester.test_get_nonexistent_classroom),
        
        # Natural Language Search tests
        ("Basic Search", tester.test_natural_language_search_basic),
        ("Floor Filter Search", tester.test_natural_language_search_floor_filter),
        ("Facility Filter Search", tester.test_natural_language_search_facility_filter),
        ("Capacity Filter Search", tester.test_natural_language_search_capacity_filter),
        ("Time Validation Search", tester.test_natural_language_search_time_validation),
        ("Complex Search", tester.test_natural_language_search_complex),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n✅ All tests passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())