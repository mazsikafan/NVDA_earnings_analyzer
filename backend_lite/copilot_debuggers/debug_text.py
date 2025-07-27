#!/usr/bin/env python3
"""
Debug what text is actually being analyzed
"""
import diskcache as dc
from services.scraper import MotleyFoolScraper
from services.parser import TranscriptParser

def debug_text_extraction():
    print("🔍 DEBUGGING TEXT EXTRACTION")
    print("=" * 60)
    
    scraper = MotleyFoolScraper()
    parser = TranscriptParser()
    
    # Get one transcript
    url = "https://www.fool.com/earnings/call-transcripts/2024/08/28/nvidia-nvda-q2-2025-earnings-call-transcript/"
    print(f"📄 Analyzing: {url}")
    
    transcript_data = scraper.scrape_transcript(url)
    if transcript_data:
        parsed = parser.parse(transcript_data)
        
        print(f"\n📝 MANAGEMENT REMARKS ({len(parsed['management_remarks'])} segments):")
        for i, segment in enumerate(parsed['management_remarks'][:3]):  # Show first 3
            print(f"\nSegment {i+1}:")
            print(f"  Speaker: {segment.get('speaker', 'Unknown')}")
            print(f"  Content preview: '{segment['content'][:150]}...'")
            print(f"  Word count: {segment.get('word_count', 0)}")
        
        # Show what gets combined for sentiment analysis
        combined_mgmt = ' '.join([seg['content'] for seg in parsed['management_remarks'][:5]])
        print(f"\n🔗 COMBINED MANAGEMENT TEXT (first 300 chars):")
        print(f"'{combined_mgmt[:300]}...'")
        
        print(f"\n💬 Q&A SESSION ({len(parsed['qa_session'])} segments):")
        executive_responses = [seg for seg in parsed['qa_session'] if seg.get('speaker_type') == 'executive']
        print(f"Executive responses: {len(executive_responses)}")
        
        for i, segment in enumerate(executive_responses[:3]):  # Show first 3 executive responses
            print(f"\nExecutive Response {i+1}:")
            print(f"  Speaker: {segment.get('speaker', 'Unknown')}")
            print(f"  Speaker type: {segment.get('speaker_type', 'Unknown')}")
            print(f"  Content preview: '{segment['content'][:150]}...'")
            print(f"  Word count: {segment.get('word_count', 0)}")
        
        # Show what gets combined for Q&A sentiment analysis
        combined_qa = ' '.join([seg['content'] for seg in executive_responses[:5]])
        print(f"\n🔗 COMBINED Q&A TEXT (first 300 chars):")
        print(f"'{combined_qa[:300]}...'")

if __name__ == "__main__":
    debug_text_extraction()
