#!/usr/bin/env python3
"""
Debug script to check token limits and text processing for FinBERT models
"""

from services.sentiment_analyzer import SentimentAnalyzer
from services.parser import TranscriptParser
from services.scraper import MotleyFoolScraper
from transformers import AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)

def analyze_token_usage():
    """Analyze token usage for FinBERT sentiment analysis"""
    
    # Initialize components
    scraper = MotleyFoolScraper()
    parser = TranscriptParser()
    analyzer = SentimentAnalyzer()
    
    # Load tokenizer to check token counts
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    
    print("=" * 80)
    print("TOKEN LIMIT ANALYSIS FOR FINBERT SENTIMENT ANALYSIS")
    print("=" * 80)
    
    # Test with Q2 2025 (the one showing positive sentiment)
    url = "https://www.fool.com/earnings/call-transcripts/2024/08/28/nvidia-nvda-q2-2025-earnings-call-transcript/"
    
    print(f"\nScraping: {url}")
    raw_html = scraper.scrape_transcript(url)
    
    if not raw_html:
        print("ERROR: Could not scrape transcript")
        return
    
    print(f"Raw HTML length: {len(raw_html):,} characters")
    
    # Parse the transcript
    parsed_data = parser.parse_transcript(raw_html, 2, 2025)
    
    print(f"\nParsed transcript:")
    print(f"- Management segments: {len(parsed_data['management_segments'])}")
    print(f"- Q&A segments: {len(parsed_data['qa_segments'])}")
    
    # Analyze management segments
    print(f"\n" + "="*50)
    print("MANAGEMENT SEGMENTS ANALYSIS")
    print("="*50)
    
    for i, segment in enumerate(parsed_data['management_segments']):
        content = segment['content']
        word_count = segment['word_count']
        
        # Count tokens
        tokens = tokenizer.encode(content, add_special_tokens=True)
        token_count = len(tokens)
        
        print(f"\nSegment {i+1}:")
        print(f"  Speaker: {segment['speaker']}")
        print(f"  Characters: {len(content):,}")
        print(f"  Words: {word_count:,}")
        print(f"  Tokens: {token_count:,}")
        print(f"  Within 512 limit: {'✓' if token_count <= 512 else '✗ EXCEEDS LIMIT'}")
        
        if token_count > 512:
            print(f"  WARNING: Text will be truncated!")
            # Show how much would be truncated
            truncated_tokens = tokenizer.encode(content, max_length=512, truncation=True, add_special_tokens=True)
            truncated_text = tokenizer.decode(truncated_tokens, skip_special_tokens=True)
            print(f"  Truncated to {len(truncated_tokens)} tokens ({len(truncated_text)} chars)")
            
        # Preview the text
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"  Preview: {preview}")
    
    # Test actual sentiment analysis on management segments
    print(f"\n" + "="*50)
    print("TESTING MANAGEMENT SENTIMENT ANALYSIS")
    print("="*50)
    
    # Filter meaningful segments like the analyzer does
    meaningful_segments = [
        seg for seg in parsed_data['management_segments'] 
        if seg['word_count'] > 50 and 
        not analyzer._is_boilerplate(seg['content'])
    ]
    
    print(f"Meaningful segments after filtering: {len(meaningful_segments)}")
    
    if meaningful_segments:
        # Combine like the analyzer does (limit to 3 segments)
        combined_text = ' '.join([seg['content'] for seg in meaningful_segments[:3]])
        cleaned_text = analyzer._clean_for_sentiment(combined_text)
        
        # Check token count of final text
        final_tokens = tokenizer.encode(cleaned_text, add_special_tokens=True)
        final_token_count = len(final_tokens)
        
        print(f"\nCombined management text:")
        print(f"  Combined length: {len(combined_text):,} characters")
        print(f"  After cleaning: {len(cleaned_text):,} characters")
        print(f"  Final tokens: {final_token_count:,}")
        print(f"  Within limit: {'✓' if final_token_count <= 512 else '✗ WILL BE TRUNCATED'}")
        
        # Test actual sentiment analysis
        result = analyzer._analyze_sentiment(cleaned_text)
        print(f"\nSentiment result: {result['sentiment']} (confidence: {result['confidence']:.3f})")
    
    # Analyze Q&A segments
    print(f"\n" + "="*50)
    print("Q&A SEGMENTS ANALYSIS")
    print("="*50)
    
    total_qa_chars = 0
    total_qa_tokens = 0
    
    for i, segment in enumerate(parsed_data['qa_segments'][:5]):  # Check first 5 Q&A segments
        content = segment['content']
        word_count = segment['word_count']
        
        # Count tokens
        tokens = tokenizer.encode(content, add_special_tokens=True)
        token_count = len(tokens)
        
        total_qa_chars += len(content)
        total_qa_tokens += token_count
        
        print(f"\nQ&A Segment {i+1}:")
        print(f"  Type: {segment['type']}")
        print(f"  Speaker: {segment.get('speaker', 'Unknown')}")
        print(f"  Characters: {len(content):,}")
        print(f"  Words: {word_count:,}")
        print(f"  Tokens: {token_count:,}")
        print(f"  Within 512 limit: {'✓' if token_count <= 512 else '✗ EXCEEDS LIMIT'}")
        
        # Preview the text
        preview = content[:150] + "..." if len(content) > 150 else content
        print(f"  Preview: {preview}")
    
    # Test Q&A sentiment analysis
    print(f"\n" + "="*50)
    print("TESTING Q&A SENTIMENT ANALYSIS")
    print("="*50)
    
    # Get meaningful Q&A segments like the analyzer does
    meaningful_qa = [
        seg for seg in parsed_data['qa_segments'] 
        if seg['word_count'] > 30 and 
        not analyzer._is_boilerplate(seg['content'])
    ]
    
    print(f"Meaningful Q&A segments after filtering: {len(meaningful_qa)}")
    
    if meaningful_qa:
        # Test a few individual segments
        for i, segment in enumerate(meaningful_qa[:3]):
            content = segment['content']
            cleaned_content = analyzer._clean_for_sentiment(content)
            
            tokens = tokenizer.encode(cleaned_content, add_special_tokens=True)
            token_count = len(tokens)
            
            print(f"\nQ&A Segment {i+1} for sentiment analysis:")
            print(f"  Original length: {len(content):,} chars")
            print(f"  After cleaning: {len(cleaned_content):,} chars")
            print(f"  Tokens: {token_count:,}")
            print(f"  Within limit: {'✓' if token_count <= 512 else '✗ WILL BE TRUNCATED'}")
            
            # Test sentiment analysis
            result = analyzer._analyze_qa_text(cleaned_content)
            print(f"  Sentiment: {result['sentiment']} (confidence: {result['confidence']:.3f})")
    
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"- Management segments are being properly processed")
    print(f"- Q&A segments are being analyzed individually")
    print(f"- Token limits: FinBERT max = 512 tokens")
    print(f"- Truncation happens automatically in tokenizer")
    print(f"- Check logs above for any segments exceeding limits")

if __name__ == "__main__":
    analyze_token_usage()
