"""
Simple test script for the lightweight backend
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_transcripts():
    """Test transcript URLs endpoint"""
    print("Testing transcript URLs endpoint...")
    response = requests.get(f"{BASE_URL}/api/transcripts/NVDA?quarters=2")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} transcripts")
        for url in data['transcript_urls']:
            print(f"  - {url}")
    print()

def test_analyze():
    """Test main analysis endpoint"""
    print("Testing analysis endpoint (this may take a minute)...")
    
    payload = {
        "ticker": "NVDA",
        "quarters": 2,
        "use_cache": False
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=payload,
        timeout=300
    )
    elapsed = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Time taken: {elapsed:.1f} seconds")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"\nAnalyzed {data['quarters_analyzed']} quarters")
        
        # Show sentiment results
        print("\nSentiment Analysis:")
        for transcript in data['transcripts']:
            print(f"\n{transcript['quarter']}:")
            print(f"  Management: {transcript['management_sentiment']['sentiment']} "
                  f"({transcript['management_sentiment']['confidence']:.2f})")
            print(f"  Q&A: {transcript['qa_sentiment']['sentiment']} "
                  f"({transcript['qa_sentiment']['confidence']:.2f})")
        
        # Show tone changes
        print("\nTone Changes:")
        print(f"  Overall trend: {data['tone_changes']['overall_trend']}")
        for change in data['tone_changes']['changes']:
            print(f"  {change['from_quarter']} → {change['to_quarter']}: {change['overall_change']}")
        
        # Show strategic focuses
        print("\nStrategic Focuses:")
        for quarter_focus in data['strategic_focuses']:
            print(f"\n{quarter_focus['quarter']}:")
            for focus in quarter_focus['focuses']:
                print(f"  - {focus['title']} ({focus['importance']})")
                print(f"    {focus['description']}")

def test_cache():
    """Test caching functionality"""
    print("\nTesting cache...")
    
    # First request (no cache)
    payload = {"ticker": "NVDA", "quarters": 1}
    
    start1 = time.time()
    response1 = requests.post(f"{BASE_URL}/api/analyze", json=payload)
    time1 = time.time() - start1
    from_cache1 = response1.json().get('from_cache', False)
    
    # Second request (should use cache)
    start2 = time.time()
    response2 = requests.post(f"{BASE_URL}/api/analyze", json=payload)
    time2 = time.time() - start2
    from_cache2 = response2.json().get('from_cache', False)
    
    print(f"First request: {time1:.1f}s (from_cache: {from_cache1})")
    print(f"Second request: {time2:.1f}s (from_cache: {from_cache2})")
    print(f"Speed improvement: {time1/time2:.1f}x")
    
    # Clear cache
    print("\nClearing cache...")
    response = requests.post(f"{BASE_URL}/api/clear-cache")
    print(f"Status: {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("NVIDIA Earnings Analyzer API Test")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_transcripts()
        test_analyze()
        test_cache()
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("   Make sure the server is running: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")