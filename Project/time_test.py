import requests
import json
from datetime import datetime, timezone, timedelta

# Test current time and search with specific times
base_url = "https://iipsrooms.preview.emergentagent.com/api"

# First register and login to get token
print("🔍 Testing time-specific searches...")

# Register a test user
register_data = {
    "name": "Time Test User",
    "email": f"timetest_{datetime.now().strftime('%H%M%S')}@iips.edu.in",
    "password": "TestPass123!",
    "role": "student"
}

response = requests.post(f"{base_url}/auth/register", json=register_data)
if response.status_code == 200:
    token = response.json()['token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test searches with specific times during campus hours
    test_queries = [
        "show me rooms available at 10 AM",
        "rooms free from 2 PM to 4 PM",
        "classrooms available now",
        "rooms on ground floor available at 11:30 AM",
        "show all available rooms right now"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        search_response = requests.post(
            f"{base_url}/search",
            json={"query": query},
            headers=headers
        )
        
        if search_response.status_code == 200:
            result = search_response.json()
            if result.get('rooms'):
                print(f"✅ Found {len(result['rooms'])} rooms")
            elif result.get('message'):
                print(f"📝 Message: {result['message']}")
            elif result.get('clarification_needed'):
                print(f"❓ Clarification: {result['clarification_needed']}")
        else:
            print(f"❌ Failed with status {search_response.status_code}")

    # Check what time the server thinks it is
    print(f"\n🕐 Server time check:")
    print(f"Current UTC time: {datetime.now(timezone.utc)}")
    print(f"Current IST time: {datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)}")
    
else:
    print(f"❌ Failed to register test user: {response.status_code}")