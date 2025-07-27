#!/usr/bin/env python3
"""
Simple debug script to check token limits for sentiment analysis
"""

import requests
import json
from transformers import AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)

def analyze_token_usage():
    """Analyze token usage by getting data from the API"""
    
    print("=" * 80)
    print("TOKEN LIMIT ANALYSIS FOR FINBERT SENTIMENT ANALYSIS")
    print("=" * 80)
    
    # Load tokenizer to check token counts
    print("Loading FinBERT tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    
    # Get data from API
    print("Fetching data from API...")
    response = requests.post('http://localhost:5000/api/analyze', 
                           json={'ticker': 'NVDA', 'quarters': 4})
    
    if response.status_code != 200:
        print(f"ERROR: API returned {response.status_code}")
        return
    
    data = response.json()['data']
    
    print(f"Analyzing {len(data['transcripts'])} transcripts...")
    
    for transcript in data['transcripts']:
        quarter = transcript['quarter']
        year = transcript['year']
        
        print(f"\n" + "="*60)
        print(f"Q{quarter} {year} - TOKEN ANALYSIS")
        print("="*60)
        
        print(f"Management sentiment: {transcript['management_sentiment']['sentiment']} "
              f"(confidence: {transcript['management_sentiment']['confidence']:.3f})")
        print(f"Q&A sentiment: {transcript['qa_sentiment']['sentiment']} "
              f"(confidence: {transcript['qa_sentiment']['confidence']:.3f})")
        
        print(f"Prepared remarks segments: {transcript['prepared_remarks_count']}")
        print(f"Q&A segments: {transcript['qa_count']}")
        
        # Now test token analysis by creating sample texts of different lengths
        print(f"\n📊 TOKEN ANALYSIS SIMULATION:")
        
        # Test various text lengths to see tokenization behavior
        test_texts = [
            "NVIDIA delivered record revenue driven by strong demand for our GPU computing platform.",
            "NVIDIA delivered record revenue this quarter driven by exceptional demand for our GPU computing platform across enterprise and cloud service providers. Data center revenue reached new highs as customers continue to invest in AI infrastructure and training capabilities.",
            "NVIDIA delivered another outstanding quarter with record revenue driven by exceptional demand for our GPU computing platform across enterprise, consumer internet, and cloud service providers. Our data center business reached new heights as organizations worldwide continue their digital transformation journeys and invest heavily in AI infrastructure, machine learning capabilities, and advanced analytics. The strength of our Hopper architecture and the anticipation for our upcoming Blackwell platform demonstrates the market's confidence in NVIDIA's technology leadership." * 3
        ]
        
        for i, text in enumerate(test_texts):
            # Count tokens
            tokens = tokenizer.encode(text, add_special_tokens=True)
            token_count = len(tokens)
            
            print(f"  Sample {i+1}: {len(text):,} chars → {token_count:,} tokens "
                  f"{'✓' if token_count <= 512 else '✗ EXCEEDS'}")
            
            if token_count > 512:
                # Show truncation
                truncated_tokens = tokenizer.encode(text, max_length=512, 
                                                  truncation=True, add_special_tokens=True)
                truncated_text = tokenizer.decode(truncated_tokens, skip_special_tokens=True)
                print(f"    → Truncated to {len(truncated_tokens)} tokens "
                      f"({len(truncated_text):,} chars)")
        
        # Test actual model input sizes that would be typical
        print(f"\n📈 TYPICAL EARNINGS CALL TEXT ANALYSIS:")
        
        # Simulate management remarks (typical combination of 2-3 segments)
        mgmt_text = """
        Good afternoon, and welcome to NVIDIA's earnings call. I'm pleased to report another record quarter with revenue of $35.1 billion, up 94% year-over-year. Data center revenue was $30.8 billion, up 112% from a year ago, driven by strong demand for our Hopper architecture GPUs.
        
        Our AI and accelerated computing platform continues to deliver exceptional performance for customers across cloud service providers, enterprise, and consumer internet companies. We're seeing tremendous adoption of generative AI applications, with customers investing heavily in training and inference infrastructure.
        
        Looking ahead, we're excited about the upcoming Blackwell platform, which offers significant performance improvements and is already seeing strong pre-orders from major customers. We expect Blackwell to contribute meaningfully to revenue in fiscal 2026.
        
        Gaming revenue was $2.9 billion, up 15% sequentially, driven by strong demand for our RTX 40 series graphics cards. Professional visualization revenue was $463 million, and automotive revenue was $346 million.
        
        Our gross margin expanded to 75.0% for the quarter, reflecting the strength of our data center business and operational efficiency improvements. We continue to invest in R&D to maintain our technology leadership in AI and accelerated computing.
        """
        
        mgmt_tokens = tokenizer.encode(mgmt_text.strip(), add_special_tokens=True)
        print(f"  Typical management text: {len(mgmt_text.strip()):,} chars → {len(mgmt_tokens):,} tokens "
              f"{'✓' if len(mgmt_tokens) <= 512 else '✗ WILL BE TRUNCATED'}")
        
        # Simulate Q&A response (individual answer)
        qa_text = """
        Thanks for the question. Looking at our data center growth, we're seeing strong demand across multiple vectors. First, cloud service providers continue to expand their AI infrastructure to support the growing number of generative AI applications their customers are building. Second, enterprise customers are increasingly adopting AI for various use cases including customer service, content generation, and business intelligence. Third, we're seeing new applications in areas like reasoning AI and agentic workflows that require significant compute resources. The diversity of demand gives us confidence in the sustainability of this growth trajectory.
        """
        
        qa_tokens = tokenizer.encode(qa_text.strip(), add_special_tokens=True)
        print(f"  Typical Q&A response: {len(qa_text.strip()):,} chars → {len(qa_tokens):,} tokens "
              f"{'✓' if len(qa_tokens) <= 512 else '✗ WILL BE TRUNCATED'}")
    
    print(f"\n" + "="*80)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*80)
    print("✅ FinBERT token limit: 512 tokens")
    print("✅ Transformers automatically truncates when max_length=512")
    print("✅ Most individual segments should fit within limits")
    print("⚠️  Combined management segments may exceed limits")
    print("⚠️  Very long Q&A responses may be truncated")
    print("\n💡 Current implementation should handle token limits properly")
    print("💡 Truncation preserves the beginning of text (most important)")
    print("💡 Consider monitoring truncation in logs for optimization")

if __name__ == "__main__":
    analyze_token_usage()
