"""
Lightweight Flask app for NVIDIA Earnings Analyzer
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import diskcache as dc
from datetime import datetime

# Load environment variables
load_dotenv()

# Import services
from services.scraper import MotleyFoolScraper
from services.parser import TranscriptParser
from services.sentiment_analyzer import SentimentAnalyzer
from services.strategic_analyzer import StrategicAnalyzer
from services.tone_analyzer import ToneAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize cache
cache_dir = os.getenv('CACHE_DIR', './cache')
cache = dc.Cache(cache_dir)

# Initialize services (lazy loading)
scraper = None
parser = None
sentiment_analyzer = None
strategic_analyzer = None
tone_analyzer = None


def get_scraper():
    global scraper
    if scraper is None:
        scraper = MotleyFoolScraper()
    return scraper


def get_parser():
    global parser
    if parser is None:
        parser = TranscriptParser()
    return parser


def get_sentiment_analyzer():
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = SentimentAnalyzer()
    return sentiment_analyzer


def get_strategic_analyzer():
    global strategic_analyzer
    if strategic_analyzer is None:
        strategic_analyzer = StrategicAnalyzer()
    return strategic_analyzer


def get_tone_analyzer():
    global tone_analyzer
    if tone_analyzer is None:
        tone_analyzer = ToneAnalyzer()
    return tone_analyzer


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.json
        ticker = data.get('ticker', 'NVDA')
        quarters = data.get('quarters', 4)
        use_cache = data.get('use_cache', True)
        
        # Check cache first
        cache_key = f'{ticker}_{quarters}_analysis'
        if use_cache and cache_key in cache:
            return jsonify({
                'status': 'success',
                'data': cache[cache_key],
                'from_cache': True
            })
        
        # Scrape transcripts
        scraper_inst = get_scraper()
        transcript_urls = scraper_inst.find_transcript_urls(ticker, quarters)
        
        if not transcript_urls:
            return jsonify({
                'status': 'error',
                'message': 'No transcripts found'
            }), 404
        
        # Process each transcript
        results = []
        parser_inst = get_parser()
        sentiment_inst = get_sentiment_analyzer()
        
        for url in transcript_urls:
            # Scrape transcript
            transcript_data = scraper_inst.scrape_transcript(url)
            if not transcript_data:
                continue
            
            # Parse transcript
            parsed = parser_inst.parse(transcript_data)
            
            # Analyze sentiment
            management_sentiment = sentiment_inst.analyze_management(parsed['management_remarks'])
            qa_sentiment = sentiment_inst.analyze_qa(parsed['qa_session'])
            
            results.append({
                'quarter': parsed['quarter'],
                'year': parsed['year'],
                'transcript_url': url,
                'management_sentiment': management_sentiment,
                'qa_sentiment': qa_sentiment,
                'prepared_remarks_count': len(parsed['management_remarks']),
                'qa_count': len(parsed['qa_session']),
                'transcript_data': parsed  # Include parsed transcript for tone analysis
            })
        
        # Analyze quarter-over-quarter tone change
        tone_inst = get_tone_analyzer()
        tone_changes = tone_inst.analyze_tone_changes(results)
        
        # Extract strategic focuses
        strategic_inst = get_strategic_analyzer()
        strategic_focuses = []
        for i, result in enumerate(results):
            # Get full transcript for strategic analysis
            transcript_data = scraper_inst.scrape_transcript(transcript_urls[i])
            focuses = strategic_inst.extract_focuses(transcript_data)
            strategic_focuses.append({
                'quarter': result['quarter'],
                'year': result['year'],
                'focuses': focuses
            })
        
        # Prepare final response (clean up transcript_data for JSON response)
        clean_results = []
        for result in results:
            clean_result = {k: v for k, v in result.items() if k != 'transcript_data'}
            clean_results.append(clean_result)
        
        analysis_results = {
            'ticker': ticker,
            'quarters_analyzed': len(results),
            'transcripts': clean_results,
            'tone_changes': tone_changes,
            'strategic_focuses': strategic_focuses,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Cache results
        if use_cache:
            cache.set(cache_key, analysis_results, expire=3600)
        
        return jsonify({
            'status': 'success',
            'data': analysis_results,
            'from_cache': False
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    """Collect raw transcript data without analysis"""
    try:
        data = request.json
        ticker = data.get('ticker', 'NVDA')
        quarters = data.get('quarters', 4)
        use_cache = data.get('use_cache', True)
        
        # Check cache first
        cache_key = f'{ticker}_{quarters}_transcripts'
        if use_cache and cache_key in cache:
            return jsonify({
                'status': 'success',
                'data': cache[cache_key],
                'from_cache': True,
                'message': f'Found {len(cache[cache_key])} cached transcripts for {ticker}'
            })
        
        # Scrape transcripts
        scraper_inst = get_scraper()
        transcript_urls = scraper_inst.find_transcript_urls(ticker, quarters)
        
        if not transcript_urls:
            return jsonify({
                'status': 'error',
                'message': 'No transcripts found'
            }), 404
        
        # Collect transcript data without analysis
        transcripts = []
        parser_inst = get_parser()
        
        for url in transcript_urls:
            # Scrape transcript
            transcript_data = scraper_inst.scrape_transcript(url)
            if not transcript_data:
                continue
            
            # Parse transcript
            parsed = parser_inst.parse(transcript_data)
            
            transcripts.append({
                'quarter': parsed['quarter'],
                'year': parsed['year'],
                'transcript_url': url,
                'prepared_remarks_count': len(parsed['management_remarks']),
                'qa_count': len(parsed['qa_session']),
                'collected_at': datetime.now().isoformat()
            })
        
        # Cache collected data
        if use_cache:
            cache.set(cache_key, transcripts, expire=3600)
        
        return jsonify({
            'status': 'success',
            'data': transcripts,
            'from_cache': False,
            'message': f'Successfully collected {len(transcripts)} transcripts for {ticker}'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/transcripts/<ticker>', methods=['GET'])
def get_transcripts():
    """Get transcript data without analysis"""
    try:
        ticker = request.view_args['ticker']
        quarters = request.args.get('quarters', 4, type=int)
        
        # Check cache first
        cache_key = f'{ticker}_{quarters}_transcripts'
        if cache_key in cache:
            return jsonify({
                'status': 'success',
                'data': cache[cache_key],
                'from_cache': True
            })
        
        # If not in cache, return empty data
        return jsonify({
            'status': 'success',
            'data': [],
            'from_cache': False
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the cache"""
    try:
        cache.clear()
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')