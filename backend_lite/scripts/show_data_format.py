"""
Show data storage format and flow through the system
"""
import json
import os
import requests
from pathlib import Path

def show_data_formats():
    print("=" * 80)
    print("DATA STORAGE AND FORMAT OVERVIEW")
    print("=" * 80)
    
    # 1. Show cache structure
    print("\n1. CACHE STORAGE (DiskCache)")
    print("-" * 40)
    print("Location: ./cache/")
    print("Format: Key-Value store with automatic serialization")
    
    cache_dir = Path("./cache")
    if cache_dir.exists():
        cache_files = list(cache_dir.iterdir())
        print(f"Cache files: {len(cache_files)} files")
        for file in cache_files[:3]:
            print(f"  - {file.name}")
    
    # 2. Show scraped data format
    print("\n\n2. SCRAPED TRANSCRIPT DATA")
    print("-" * 40)
    print("Format: Dictionary (in-memory)")
    
    sample_scraped = {
        "url": "https://www.fool.com/earnings/...",
        "title": "Nvidia (NVDA) Q3 2025 Earnings Call Transcript",
        "quarter": 3,
        "year": 2025,
        "full_text": "Full transcript text here...",
        "scraped_at": "2025-07-27T21:00:00"
    }
    print(json.dumps(sample_scraped, indent=2))
    
    # 3. Show parsed transcript format
    print("\n\n3. PARSED TRANSCRIPT DATA")
    print("-" * 40)
    print("Format: Dictionary with segmented content")
    
    sample_parsed = {
        "quarter": 3,
        "year": 2025,
        "title": "Nvidia (NVDA) Q3 2025 Earnings Call Transcript",
        "url": "https://www.fool.com/earnings/...",
        "management_remarks": [
            {
                "speaker": "Jensen Huang",
                "content": "Good afternoon everyone...",
                "word_count": 450
            },
            {
                "speaker": "Colette Kress",
                "content": "Thank you Jensen...",
                "word_count": 380
            }
        ],
        "qa_session": [
            {
                "speaker": "Analyst - Bank of America",
                "content": "Thanks for taking my question...",
                "word_count": 85,
                "speaker_type": "analyst"
            },
            {
                "speaker": "Jensen Huang",
                "content": "Great question...",
                "word_count": 220,
                "speaker_type": "executive"
            }
        ],
        "total_segments": 25
    }
    print(json.dumps(sample_parsed, indent=2))
    
    # 4. Show sentiment analysis format
    print("\n\n4. SENTIMENT ANALYSIS DATA")
    print("-" * 40)
    print("Format: Dictionary with scores")
    
    sample_sentiment = {
        "sentiment": "positive",
        "confidence": 0.994,
        "scores": {
            "positive": 0.994,
            "neutral": 0.006,
            "negative": 0.000
        }
    }
    print(json.dumps(sample_sentiment, indent=2))
    
    # 5. Show complete API response format
    print("\n\n5. COMPLETE API RESPONSE FORMAT")
    print("-" * 40)
    print("Format: JSON response from /api/analyze endpoint")
    
    sample_response = {
        "status": "success",
        "from_cache": False,
        "data": {
            "ticker": "NVDA",
            "quarters_analyzed": 2,
            "analysis_timestamp": "2025-07-27T21:50:20.344223",
            "transcripts": [
                {
                    "quarter": 3,
                    "year": 2025,
                    "transcript_url": "https://...",
                    "management_sentiment": {
                        "sentiment": "neutral",
                        "confidence": 0.926,
                        "scores": {"positive": 0.034, "neutral": 0.926, "negative": 0.039}
                    },
                    "qa_sentiment": {
                        "sentiment": "positive",
                        "confidence": 0.999,
                        "scores": {"positive": 0.999, "neutral": 0.001, "negative": 0.000}
                    },
                    "prepared_remarks_count": 2,
                    "qa_count": 31
                }
            ],
            "tone_changes": {
                "overall_trend": "mixed",
                "summary": "NVIDIA's tone has shown mixed signals...",
                "changes": [
                    {
                        "from_quarter": "Q2 2025",
                        "to_quarter": "Q3 2025",
                        "management_tone_change": "stable",
                        "qa_tone_change": "improving",
                        "overall_change": "improving",
                        "score_change": 0.395
                    }
                ]
            },
            "strategic_focuses": [
                {
                    "quarter": 3,
                    "year": 2025,
                    "focuses": [
                        {
                            "title": "Data Center Expansion",
                            "description": "Achieved record revenue...",
                            "importance": "high"
                        }
                    ]
                }
            ]
        }
    }
    
    print(json.dumps(sample_response, indent=2))
    
    # 6. Show cache key format
    print("\n\n6. CACHE KEY FORMAT")
    print("-" * 40)
    print("Format: {ticker}_{quarters}_analysis")
    print("Examples:")
    print("  - NVDA_4_analysis")
    print("  - NVDA_2_analysis")
    print("  - AAPL_4_analysis")
    
    # 7. Make actual API call to show real data
    print("\n\n7. ACTUAL STORED DATA SAMPLE")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:5000/api/transcripts/NVDA?quarters=1")
        if response.status_code == 200:
            print("Real transcript URLs from API:")
            print(json.dumps(response.json(), indent=2))
    except:
        print("(Server not running - showing sample format)")
    
    # 8. Show data flow
    print("\n\n8. DATA FLOW THROUGH SYSTEM")
    print("-" * 40)
    print("""
    1. Web Scraping (scraper.py)
       ↓ Returns: Dict with full_text
    2. Text Parsing (parser.py)
       ↓ Returns: Dict with management_remarks + qa_session arrays
    3. Sentiment Analysis (sentiment_analyzer.py)
       ↓ Returns: Dict with sentiment scores for each section
    4. Tone Analysis (tone_analyzer.py)
       ↓ Returns: Dict with quarter-over-quarter changes
    5. Strategic Focus (strategic_analyzer.py)
       ↓ Returns: Array of focus objects
    6. Cache Storage (diskcache)
       ↓ Stores: Complete analysis results
    7. API Response (Flask)
       Returns: JSON with all analysis results
    """)

if __name__ == "__main__":
    show_data_formats()