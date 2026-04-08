
import requests
import time

GATEWAY_URL = "http://localhost:8000"
API_KEY = "test_key_123"

def test_gateway():
    print("--- Testing API Gateway ---")
    
    # 1. Test Proxying
    print("\n1. Testing Proxy to News Service...")
    try:
        resp = requests.get(f"{GATEWAY_URL}/api/news/latest", headers={"x-api-key": API_KEY})
        print(f"Status: {resp.status_code}, Body: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}. Is the gateway running?")

    # 2. Test Caching (Repeat the request)
    print("\n2. Testing Cache Hit (Requesting same URL again)...")
    resp = requests.get(f"{GATEWAY_URL}/api/news/latest", headers={"x-api-key": API_KEY})
    print(f"Status: {resp.status_code} (Should be fast - check Gateway logs for 'CACHE HIT')")

    # 3. Test Rate Limiting
    print("\n3. Testing Rate Limiting (Spamming 100 requests)...")
    for i in range(100):
        resp = requests.get(f"{GATEWAY_URL}/api/weather", headers={"x-api-key": "spam_key"})
        if resp.status_code == 429:
            print(f"Request {i+1}: Blocked by Rate Limiter as expected ({resp.json()['error']})")
            break
    else:
        print("Rate limiter did not trigger even after 100 requests. Check limits in config.")

    # 4. Test Health Check
    print("\n4. Testing Health Check Dashboard Data...")
    resp = requests.get(f"{GATEWAY_URL}/api/health-metrics")
    print(f"Health Data: {resp.json()}")

    # 5. Test Circuit Breaker
    print("\n5. Testing Circuit Breaker (Using 'broken' key on News service)...")
    for i in range(6):
        try:
            # We use a valid URL, but the 'broken' key forces a failure inside the Gateway
            resp = requests.get(f"{GATEWAY_URL}/api/news", headers={"x-api-key": "broken"})
            status = resp.status_code
            error_data = resp.json()
            error_msg = error_data.get("error", "Unknown")
            print(f"Request {i+1}: Status {status} ({error_msg})")
            if status == 503:
                print("SUCCESS: Circuit Breaker is now OPEN for News Service!")
                break
        except Exception as e:
            print(f"Request {i+1} failed completely: {e}")
    else:
        print("FAILED: Circuit Breaker did not open after 6 failures.")

if __name__ == "__main__":
    test_gateway()
