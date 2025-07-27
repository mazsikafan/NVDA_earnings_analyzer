"""
Generate a formatted report from the 4 signal extractions
"""
import requests
import json
from datetime import datetime

def generate_report():
    """Fetch analysis and generate formatted report"""
    
    # Fetch analysis from API
    print("Fetching NVIDIA earnings analysis...")
    response = requests.post(
        "http://localhost:5000/api/analyze",
        json={"ticker": "NVDA", "quarters": 4, "use_cache": True}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    
    data = response.json()['data']
    
    # Generate formatted report
    print("\n" + "=" * 80)
    print("NVIDIA EARNINGS CALL ANALYSIS REPORT")
    print("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    print(f"\nAnalyzed {data['quarters_analyzed']} quarters for ticker: {data['ticker']}")
    print("-" * 80)
    
    # 1. Management Sentiment Analysis
    print("\n📊 SIGNAL 1: MANAGEMENT SENTIMENT (FinBERT Analysis)")
    print("-" * 50)
    for transcript in data['transcripts']:
        quarter = f"Q{transcript['quarter']} {transcript['year']}"
        sentiment = transcript['management_sentiment']
        print(f"\n{quarter}:")
        print(f"  Sentiment: {sentiment['sentiment'].upper()}")
        print(f"  Confidence: {sentiment['confidence']:.1%}")
        print(f"  Breakdown:")
        print(f"    - Positive: {sentiment['scores']['positive']:.1%}")
        print(f"    - Neutral:  {sentiment['scores']['neutral']:.1%}")
        print(f"    - Negative: {sentiment['scores']['negative']:.1%}")
    
    # 2. Q&A Sentiment Analysis
    print("\n\n💬 SIGNAL 2: Q&A SESSION SENTIMENT (FinBERT-tone Analysis)")
    print("-" * 50)
    for transcript in data['transcripts']:
        quarter = f"Q{transcript['quarter']} {transcript['year']}"
        sentiment = transcript['qa_sentiment']
        print(f"\n{quarter}:")
        print(f"  Sentiment: {sentiment['sentiment'].upper()}")
        print(f"  Confidence: {sentiment['confidence']:.1%}")
        print(f"  Breakdown:")
        print(f"    - Positive: {sentiment['scores']['positive']:.1%}")
        print(f"    - Neutral:  {sentiment['scores']['neutral']:.1%}")
        print(f"    - Negative: {sentiment['scores']['negative']:.1%}")
        print(f"  Q&A Exchanges: {transcript['qa_count']}")
    
    # 3. Quarter-over-Quarter Tone Change
    print("\n\n📈 SIGNAL 3: QUARTER-OVER-QUARTER TONE CHANGE")
    print("-" * 50)
    tone_data = data['tone_changes']
    print(f"\nOverall Trend: {tone_data['overall_trend'].upper().replace('_', ' ')}")
    print(f"Summary: {tone_data['summary']}")
    
    if tone_data['changes']:
        print("\nDetailed Changes:")
        for change in tone_data['changes']:
            print(f"\n{change['from_quarter']} → {change['to_quarter']}:")
            print(f"  - Management Tone: {change['management_tone_change'].upper()}")
            print(f"  - Q&A Tone: {change['qa_tone_change'].upper()}")
            print(f"  - Overall Change: {change['overall_change'].upper()}")
            print(f"  - Score Delta: {change['score_change']:+.3f}")
    
    # 4. Strategic Focuses
    print("\n\n🎯 SIGNAL 4: STRATEGIC FOCUSES (AI-Extracted Key Themes)")
    print("-" * 50)
    for quarter_focus in data['strategic_focuses']:
        quarter = f"Q{quarter_focus['quarter']} {quarter_focus['year']}"
        print(f"\n{quarter} Key Strategic Themes:")
        for i, focus in enumerate(quarter_focus['focuses'], 1):
            print(f"\n  {i}. {focus['title']} [{focus['importance'].upper()}]")
            print(f"     {focus['description']}")
    
    # Summary Dashboard
    print("\n\n" + "=" * 80)
    print("EXECUTIVE SUMMARY DASHBOARD")
    print("=" * 80)
    
    # Calculate averages
    mgmt_sentiments = [t['management_sentiment']['sentiment'] for t in data['transcripts']]
    qa_sentiments = [t['qa_sentiment']['sentiment'] for t in data['transcripts']]
    
    # Count sentiments
    mgmt_positive = sum(1 for s in mgmt_sentiments if s == 'positive')
    mgmt_neutral = sum(1 for s in mgmt_sentiments if s == 'neutral')
    mgmt_negative = sum(1 for s in mgmt_sentiments if s == 'negative')
    
    qa_positive = sum(1 for s in qa_sentiments if s == 'positive')
    qa_neutral = sum(1 for s in qa_sentiments if s == 'neutral')
    qa_negative = sum(1 for s in qa_sentiments if s == 'negative')
    
    print("\n📊 Sentiment Overview:")
    print(f"  Management: {mgmt_positive} positive, {mgmt_neutral} neutral, {mgmt_negative} negative")
    print(f"  Q&A Session: {qa_positive} positive, {qa_neutral} neutral, {qa_negative} negative")
    
    print(f"\n📈 Tone Trend: {tone_data['overall_trend'].upper().replace('_', ' ')}")
    
    # Top strategic themes
    print("\n🎯 Top Strategic Themes Across All Quarters:")
    all_themes = {}
    for qf in data['strategic_focuses']:
        for focus in qf['focuses']:
            theme = focus['title']
            if theme not in all_themes:
                all_themes[theme] = 0
            all_themes[theme] += 1
    
    sorted_themes = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)
    for theme, count in sorted_themes[:5]:
        print(f"  - {theme} (mentioned in {count} quarters)")
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)

if __name__ == "__main__":
    generate_report()