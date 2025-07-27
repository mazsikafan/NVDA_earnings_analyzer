"""
Inspect the actual cache contents
"""
import diskcache as dc
import json
from datetime import datetime

def inspect_cache():
    print("=" * 80)
    print("CACHE INSPECTION")
    print("=" * 80)
    
    # Open cache
    cache = dc.Cache('./cache')
    
    # Show cache stats
    print("\nCache Statistics:")
    print(f"  Total items: {len(cache)}")
    print(f"  Cache size: {cache.volume() / 1024:.1f} KB")
    
    # List all keys
    print("\nCached Keys:")
    for key in cache.iterkeys():
        print(f"  - {key}")
    
    # Show sample cached data
    print("\nSample Cached Data:")
    print("-" * 40)
    
    # Get one cached item
    sample_key = 'NVDA_2_analysis'
    if sample_key in cache:
        data = cache[sample_key]
        
        # Show structure
        print(f"\nKey: {sample_key}")
        print(f"Type: {type(data)}")
        print(f"Top-level keys: {list(data.keys())}")
        
        # Show transcript structure
        if 'transcripts' in data and data['transcripts']:
            print(f"\nNumber of transcripts: {len(data['transcripts'])}")
            transcript = data['transcripts'][0]
            print(f"Transcript keys: {list(transcript.keys())}")
            
            # Show sentiment data
            print(f"\nManagement Sentiment:")
            print(f"  {json.dumps(transcript['management_sentiment'], indent=2)}")
            
            print(f"\nQ&A Sentiment:")
            print(f"  {json.dumps(transcript['qa_sentiment'], indent=2)}")
        
        # Show strategic focuses
        if 'strategic_focuses' in data and data['strategic_focuses']:
            print(f"\nStrategic Focuses for Q{data['strategic_focuses'][0]['quarter']}:")
            for focus in data['strategic_focuses'][0]['focuses']:
                print(f"  - {focus['title']} [{focus['importance']}]")
    
    # Show cache expiration
    print("\n\nCache Configuration:")
    print(f"  Cache timeout: 3600 seconds (1 hour)")
    print(f"  Storage format: SQLite database")
    print(f"  Serialization: Automatic (pickle)")
    
    cache.close()

if __name__ == "__main__":
    inspect_cache()