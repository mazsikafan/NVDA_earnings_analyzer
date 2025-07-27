#!/usr/bin/env python3
"""
Test the improved sentiment analysis directly
"""
import requests
import json

def test_fresh_analysis():
    print("🧪 TESTING FRESH ANALYSIS WITH IMPROVED TEXT PROCESSING")
    print("=" * 70)
    
    # Clear cache first
    try:
        response = requests.post('http://localhost:5000/api/clear-cache')
        print(f"✅ Cache cleared: {response.json()}")
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return
    
    # Trigger fresh analysis
    try:
        print("\n🚀 Triggering fresh analysis...")
        response = requests.post('http://localhost:5000/api/analyze', 
                               json={'ticker': 'NVDA', 'quarters': 4, 'use_cache': False})
        
        if response.status_code == 200:
            data = response.json()['data']
            
            print(f"\n📊 FRESH ANALYSIS RESULTS:")
            print(f"Analyzed {data['quarters_analyzed']} quarters")
            
            for transcript in data['transcripts']:
                print(f"\n📈 Q{transcript['quarter']} {transcript['year']}:")
                mgmt = transcript['management_sentiment']
                qa = transcript['qa_sentiment']
                
                print(f"   🎯 Management: {mgmt['sentiment']} (conf: {mgmt['confidence']:.3f})")
                print(f"      Scores: pos={mgmt['scores']['positive']:.3f}, neg={mgmt['scores']['negative']:.3f}, neu={mgmt['scores']['neutral']:.3f}")
                
                print(f"   💬 Q&A: {qa['sentiment']} (conf: {qa['confidence']:.3f})")
                print(f"      Scores: pos={qa['scores']['positive']:.3f}, neg={qa['scores']['negative']:.3f}, neu={qa['scores']['neutral']:.3f}")
                
                print(f"   📝 Text counts: {transcript['prepared_remarks_count']} mgmt, {transcript['qa_count']} Q&A")
            
            # Show tone changes
            if 'tone_changes' in data:
                print(f"\n📈 TONE CHANGES:")
                for change in data['tone_changes']:
                    print(f"   {change}")
                    
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    test_fresh_analysis()
