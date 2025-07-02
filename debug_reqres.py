# debug_reqres.py - Debug ReqRes API Issues
import requests
import json

def test_reqres_directly():
    """Test ReqRes API directly to understand the issue"""
    base_url = "https://reqres.in/api"
    
    print("🔍 DEBUGGING REQRES API ISSUES")
    print("=" * 50)
    
    # Test 1: Simple GET request
    print("\n1. Testing GET /users...")
    try:
        response = requests.get(f"{base_url}/users")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success! Found {len(data.get('data', []))} users")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: GET with page parameter
    print("\n2. Testing GET /users?page=1...")
    try:
        response = requests.get(f"{base_url}/users", params={'page': 1})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success! Page {data.get('page')}, {len(data.get('data', []))} users")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: POST create user with different approaches
    print("\n3. Testing POST /users (JSON)...")
    user_data = {"name": "John Doe", "job": "QA Engineer"}
    
    try:
        response = requests.post(
            f"{base_url}/users",
            json=user_data,  # Using json parameter
            headers={'Accept': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   Success! Created user: {response.json()}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: POST with manual JSON
    print("\n4. Testing POST /users (Manual JSON)...")
    try:
        response = requests.post(
            f"{base_url}/users",
            data=json.dumps(user_data),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   Success! Created user: {response.json()}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 5: PUT update user
    print("\n5. Testing PUT /users/2...")
    update_data = {"name": "Jane Smith", "job": "Senior QA"}
    
    try:
        response = requests.put(
            f"{base_url}/users/2",
            json=update_data,
            headers={'Accept': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Success! Updated user: {response.json()}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS COMPLETE")

if __name__ == "__main__":
    test_reqres_directly()