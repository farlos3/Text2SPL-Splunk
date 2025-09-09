"""
Test script for SPL API endpoints
"""
import json
import requests
import time

BASE_URL = "http://localhost:8000/api/spl"

def test_service_status():
    """Test SPL service status endpoint"""
    print("Testing service status...")
    try:
        response = requests.get(f"{BASE_URL}/service-status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_check_relevance():
    """Test relevance checking endpoint"""
    print("\nTesting relevance check...")
    
    test_queries = [
        "Show all failed login attempts in the last 24 hours",
        "What's the weather like today?",
        "Find suspicious authentication events",
        "How to cook pasta?"
    ]
    
    for query in test_queries:
        try:
            payload = {"query": query, "verbose": False}
            response = requests.post(f"{BASE_URL}/check-relevance", json=payload)
            result = response.json()
            
            print(f"Query: {query}")
            print(f"  Splunk-related: {result.get('is_splunk_related', False)}")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
            print(f"  Method: {result.get('method', 'unknown')}")
            print()
        except Exception as e:
            print(f"Error with query '{query}': {e}")

def test_generate_spl():
    """Test SPL generation endpoint"""
    print("\nTesting SPL generation...")
    
    test_queries = [
        "Show all failed login attempts in the last 24 hours",
        "Find service changes in Windows systems",
        "Monitor network connection trends by hour"
    ]
    
    for query in test_queries:
        try:
            payload = {"query": query, "verbose": False}
            response = requests.post(f"{BASE_URL}/generate-spl", json=payload)
            result = response.json()
            
            print(f"Query: {query}")
            print(f"  Success: {result.get('success', False)}")
            if result.get('success'):
                print(f"  Company: {result.get('company', 'Unknown')}")
                print(f"  Index: {result.get('index', 'Unknown')}")
                print(f"  Confidence: {result.get('confidence', 0):.2f}")
                print(f"  SPL Query:\n{result.get('spl_query', 'None')}")
                if result.get('issues'):
                    print(f"  Issues: {result['issues']}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
            print("-" * 50)
        except Exception as e:
            print(f"Error with query '{query}': {e}")

def main():
    """Run all tests"""
    print("Starting SPL API tests...")
    print("=" * 60)
    
    # Test service status first
    if not test_service_status():
        print("Service status test failed. Stopping tests.")
        return
    
    # Give service time to initialize
    print("\nWaiting for service initialization...")
    time.sleep(2)
    
    # Test other endpoints
    test_check_relevance()
    test_generate_spl()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()
