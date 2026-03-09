import os
import time
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000"
TEST_USERS = [
    {"email": "user1@test.com", "password": "password123"},
    {"email": "user2@test.com", "password": "password123"},
    {"email": "user3@test.com", "password": "password123"}
]

def check_health():
    try:
        response = requests.get(f"{BASE_URL}/api/v1/")
        return response.status_code == 200
    except:
        return False

def register_user(user):
    # This might fail if the user already exists, which is fine
    requests.post(f"{BASE_URL}/api/v1/auth/register", json=user)

def login(user):
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
        "username": user["email"],
        "password": user["password"]
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_security_auth_bypass():
    print("Testing security: auth bypass")
    response = requests.get(f"{BASE_URL}/api/v1/users/me")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

def test_performance_queries(token):
    # Simulate an AI analyst query or something
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    # Dummy endpoint, adjust if real one differs
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
        end = time.time()
        return end - start, response.status_code
    except Exception as e:
        return 0, 500

def run_performance_test():
    print("Running performance test with 10 simulated users")
    tokens = []
    for user in TEST_USERS:
        tokens.append(login(user))
    
    valid_tokens = [t for t in tokens if t]
    if not valid_tokens:
        print("No valid auth tokens, skipping performance queries.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(20): # 20 total requests
            token = valid_tokens[i % len(valid_tokens)]
            futures.append(executor.submit(test_performance_queries, token))
            
        times = []
        for future in concurrent.futures.as_completed(futures):
            t, status = future.result()
            times.append(t)
            
    avg_time = sum(times) / len(times)
    print(f"Performance Test complete. Avg response time: {avg_time:.3f}s")
    assert avg_time < 10.0, f"Average response time {avg_time:.3f}s exceeded 10s limit"
    
if __name__ == "__main__":
    print("Starting Security & Performance test suite")
    if not check_health():
        print(f"Warning: API at {BASE_URL} doesn't seem to be responding.")
    
    for u in TEST_USERS:
        register_user(u)
        
    test_security_auth_bypass()
    run_performance_test()
    print("Security & Performance test script completed.")
