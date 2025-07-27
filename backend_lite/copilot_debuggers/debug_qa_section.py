#!/usr/bin/env python3
"""
Find the actual Q&A section start in the transcript
"""
from services.scraper import MotleyFoolScraper

def find_qa_section():
    print("🔍 FINDING ACTUAL Q&A SECTION")
    print("=" * 60)
    
    scraper = MotleyFoolScraper()
    
    url = "https://www.fool.com/earnings/call-transcripts/2024/08/28/nvidia-nvda-q2-2025-earnings-call-transcript/"
    transcript_data = scraper.scrape_transcript(url)
    
    if transcript_data:
        full_text = transcript_data.get('full_text', '')
        
        # Look for actual Q&A patterns throughout the text
        import re
        
        qa_patterns = [
            r'Thank you\.\s*\[Operator instructions\]\s*And your first question',
            r'And your first question comes from',
            r'Our first question comes from',
            r'Thank you\.\s*And our first question',
            r'We are going to open up the call.*to questions',
            r'operator.*questions',
            r'first question'
        ]
        
        print("🔍 Searching for Q&A section markers:")
        
        for pattern in qa_patterns:
            matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
            if matches:
                for match in matches:
                    pos = match.start()
                    context_start = max(0, pos - 200)
                    context_end = min(len(full_text), pos + 300)
                    
                    print(f"\n✅ Found pattern '{pattern}' at position {pos}:")
                    print("=" * 60)
                    print(full_text[context_start:context_end])
                    print("=" * 60)
                    
                    return pos  # Return first match
        
        # If no specific patterns found, search for common analyst names
        analyst_patterns = [
            r'C\.J\. Muse.*Analyst',
            r'Harsh Kumar.*Analyst', 
            r'Timothy Arcuri.*Analyst',
            r'Vivek Arya.*Analyst'
        ]
        
        print("\n🔍 Searching for analyst names:")
        
        for pattern in analyst_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                pos = match.start()
                context_start = max(0, pos - 200)
                context_end = min(len(full_text), pos + 300)
                
                print(f"\n✅ Found analyst pattern '{pattern}' at position {pos}:")
                print("=" * 60)
                print(full_text[context_start:context_end])
                print("=" * 60)
                
                return pos
    
    return -1

if __name__ == "__main__":
    find_qa_section()
