#!/usr/bin/env python3
"""
Debug sentiment analysis to understand why results seem uniform
"""
import diskcache as dc
import json
from services.sentiment_analyzer import SentimentAnalyzer
from services.scraper import MotleyFoolScraper
from services.parser import TranscriptParser

def debug_sentiment():
    print("🔍 DEBUGGING SENTIMENT ANALYSIS")
    print("=" * 60)
    
    # Load cached data
    cache = dc.Cache('./cache')
    if 'NVDA_4_analysis' in cache:
        data = cache['NVDA_4_analysis']
        print(f"📊 Found cached data with {len(data['transcripts'])} transcripts")
        
        for i, transcript in enumerate(data['transcripts']):
            print(f"\n📈 Q{transcript['quarter']} {transcript['year']}:")
            print(f"   Management: {transcript['management_sentiment']['sentiment']} ({transcript['management_sentiment']['confidence']:.3f})")
            print(f"   Raw scores: {transcript['management_sentiment']['scores']}")
            print(f"   Q&A: {transcript['qa_sentiment']['sentiment']} ({transcript['qa_sentiment']['confidence']:.3f})")
            print(f"   Raw scores: {transcript['qa_sentiment']['scores']}")
    
    print("\n" + "=" * 60)
    print("🧪 TESTING FRESH ANALYSIS ON SAMPLE TEXT")
    
    # Test with different sample texts
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "We delivered record revenue and outstanding performance this quarter.",
        "We face significant challenges and declining demand in several markets.",
        "Revenue was flat compared to last quarter with mixed results.",
        "Wow, this is absolutely amazing growth! Our stock is through the roof!",
        "This is terrible news. We're seeing massive losses and layoffs."
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\nTest {i+1}: '{text[:50]}...'")
        result = analyzer._analyze_text(text, f"Test {i+1}")
        print(f"  Result: {result['sentiment']} (confidence: {result['confidence']:.3f})")
        print(f"  Scores: pos={result['scores']['positive']:.3f}, neg={result['scores']['negative']:.3f}, neu={result['scores']['neutral']:.3f}")
        
        qa_result = analyzer._analyze_qa_text(text)
        print(f"  Q&A Model: {qa_result['sentiment']} (confidence: {qa_result['confidence']:.3f})")
        print(f"  Q&A Scores: pos={qa_result['scores']['positive']:.3f}, neg={qa_result['scores']['negative']:.3f}, neu={qa_result['scores']['neutral']:.3f}")

    print("\n" + "=" * 60)
    print("🔍 ANALYZING ACTUAL TRANSCRIPT CONTENT")
    
    # Let's look at the actual content being analyzed
    scraper = MotleyFoolScraper()
    parser = TranscriptParser()
    
    # Get one transcript
    url = "https://www.fool.com/earnings/call-transcripts/2024/08/28/nvidia-nvda-q2-2025-earnings-call-transcript/"
    print(f"\n📄 Analyzing: {url}")
    
    transcript_data = scraper.scrape_transcript(url)
    if transcript_data:
        parsed = parser.parse(transcript_data)
        
        print(f"\n📝 Management remarks count: {len(parsed['management_remarks'])}")
        if parsed['management_remarks']:
            sample_mgmt = parsed['management_remarks'][0]['content'][:200]
            print(f"Sample management text: '{sample_mgmt}...'")
            
            mgmt_result = analyzer.analyze_management(parsed['management_remarks'])
            print(f"Management analysis: {mgmt_result}")
        
        print(f"\n💬 Q&A segments count: {len(parsed['qa_session'])}")
        if parsed['qa_session']:
            executive_responses = [seg for seg in parsed['qa_session'] if seg.get('speaker_type') == 'executive']
            print(f"Executive responses: {len(executive_responses)}")
            
            if executive_responses:
                sample_qa = executive_responses[0]['content'][:200]
                print(f"Sample Q&A text: '{sample_qa}...'")
            
            qa_result = analyzer.analyze_qa(parsed['qa_session'])
            print(f"Q&A analysis: {qa_result}")

if __name__ == "__main__":
    debug_sentiment()
