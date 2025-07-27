#!/usr/bin/env python3
"""
Debug the raw transcript structure to understand the issue
"""
from services.scraper import MotleyFoolScraper

def debug_raw_transcript():
    print("🔍 DEBUGGING RAW TRANSCRIPT STRUCTURE")
    print("=" * 60)
    
    scraper = MotleyFoolScraper()
    
    # Get one transcript
    url = "https://www.fool.com/earnings/call-transcripts/2024/08/28/nvidia-nvda-q2-2025-earnings-call-transcript/"
    print(f"📄 Analyzing: {url}")
    
    transcript_data = scraper.scrape_transcript(url)
    if transcript_data:
        full_text = transcript_data.get('full_text', '')
        
        print(f"📝 Full text length: {len(full_text)} characters")
        print(f"📝 Full text preview (first 1000 chars):")
        print("=" * 60)
        print(full_text[:1000])
        print("=" * 60)
        
        # Find section markers
        text_lower = full_text.lower()
        
        prepared_pos = text_lower.find('prepared remarks')
        qa_pos = text_lower.find('questions and answers')
        
        print(f"\n📍 Section positions:")
        print(f"  'Prepared Remarks' found at: {prepared_pos}")
        print(f"  'Questions and Answers' found at: {qa_pos}")
        
        if prepared_pos >= 0:
            # Show content around prepared remarks
            start = max(0, prepared_pos - 100)
            end = min(len(full_text), prepared_pos + 500)
            print(f"\n🎯 CONTENT AROUND 'PREPARED REMARKS':")
            print("=" * 60)
            print(full_text[start:end])
            print("=" * 60)
        
        if qa_pos >= 0:
            # Show content around Q&A
            start = max(0, qa_pos - 100)
            end = min(len(full_text), qa_pos + 500)
            print(f"\n💬 CONTENT AROUND 'QUESTIONS AND ANSWERS':")
            print("=" * 60)
            print(full_text[start:end])
            print("=" * 60)

if __name__ == "__main__":
    debug_raw_transcript()
