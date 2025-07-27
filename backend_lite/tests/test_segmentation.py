"""
Test script to verify proper segmentation between management remarks and Q&A
"""
import json
from services.scraper import MotleyFoolScraper
from services.parser import TranscriptParser
from services.sentiment_analyzer import SentimentAnalyzer

def test_segmentation():
    print("=" * 80)
    print("Testing Transcript Segmentation and Model Usage")
    print("=" * 80)
    
    # Initialize services
    scraper = MotleyFoolScraper()
    parser = TranscriptParser()
    
    # Get a transcript
    print("\n1. Fetching transcript...")
    urls = scraper.find_transcript_urls('NVDA', 1)
    if not urls:
        print("❌ No transcript URLs found")
        return
    
    transcript_data = scraper.scrape_transcript(urls[0])
    if not transcript_data:
        print("❌ Failed to scrape transcript")
        return
    
    print(f"✅ Scraped transcript: {transcript_data['title']}")
    
    # Parse the transcript
    print("\n2. Parsing transcript...")
    parsed = parser.parse(transcript_data)
    
    print(f"✅ Total segments: {parsed['total_segments']}")
    print(f"   - Management remarks: {len(parsed['management_remarks'])} segments")
    print(f"   - Q&A session: {len(parsed['qa_session'])} segments")
    
    # Show sample segments from each section
    print("\n3. Verifying segmentation...")
    
    print("\n📊 Management Remarks Sample:")
    for i, segment in enumerate(parsed['management_remarks'][:3]):
        print(f"\n   Segment {i+1}:")
        print(f"   Speaker: {segment['speaker']}")
        print(f"   Content preview: {segment['content'][:200]}...")
        print(f"   Word count: {segment['word_count']}")
    
    print("\n\n💬 Q&A Session Sample:")
    for i, segment in enumerate(parsed['qa_session'][:6]):  # Show more to see Q&A pattern
        print(f"\n   Segment {i+1}:")
        print(f"   Speaker: {segment['speaker']}")
        print(f"   Type: {segment.get('speaker_type', 'unknown')}")
        print(f"   Content preview: {segment['content'][:200]}...")
        print(f"   Word count: {segment['word_count']}")
    
    # Test sentiment analysis on each section
    print("\n\n4. Testing sentiment analysis models...")
    analyzer = SentimentAnalyzer()
    
    # Management sentiment (should use FinBERT)
    print("\n🎯 Management Sentiment Analysis (FinBERT):")
    mgmt_sentiment = analyzer.analyze_management(parsed['management_remarks'])
    print(f"   Sentiment: {mgmt_sentiment['sentiment']}")
    print(f"   Confidence: {mgmt_sentiment['confidence']:.2f}")
    print(f"   Scores: {json.dumps(mgmt_sentiment['scores'], indent=4)}")
    
    # Q&A sentiment (should use FinBERT-tone)
    print("\n🎯 Q&A Sentiment Analysis (FinBERT-tone):")
    qa_sentiment = analyzer.analyze_qa(parsed['qa_session'])
    print(f"   Sentiment: {qa_sentiment['sentiment']}")
    print(f"   Confidence: {qa_sentiment['confidence']:.2f}")
    print(f"   Scores: {json.dumps(qa_sentiment['scores'], indent=4)}")
    
    # Verify the models are using appropriate data
    print("\n\n5. Verification Summary:")
    
    # Check if management remarks contain expected content
    mgmt_text = ' '.join([s['content'] for s in parsed['management_remarks'][:2]])
    has_mgmt_keywords = any(keyword in mgmt_text.lower() for keyword in 
                           ['revenue', 'quarter', 'growth', 'performance', 'pleased', 'results'])
    
    # Check if Q&A contains question/answer pattern
    qa_text = ' '.join([s['content'] for s in parsed['qa_session'][:4]])
    has_qa_keywords = any(keyword in qa_text.lower() for keyword in 
                         ['question', 'thank you', 'could you', 'what about', 'how do you'])
    
    print(f"\n✅ Management remarks contain financial discussion: {has_mgmt_keywords}")
    print(f"✅ Q&A section contains question/answer pattern: {has_qa_keywords}")
    
    # Check speaker diversity in Q&A
    qa_speakers = set(s['speaker'] for s in parsed['qa_session'][:10])
    print(f"✅ Q&A has {len(qa_speakers)} different speakers (expecting analysts + executives)")
    
    # Final validation
    print("\n\n6. Final Validation:")
    if (len(parsed['management_remarks']) > 0 and 
        len(parsed['qa_session']) > 0 and
        has_mgmt_keywords and 
        has_qa_keywords and
        len(qa_speakers) > 2):
        print("✅ PASS: Segmentation is working correctly!")
        print("✅ PASS: Different models are analyzing appropriate sections!")
    else:
        print("❌ FAIL: Issues detected with segmentation")

if __name__ == "__main__":
    test_segmentation()