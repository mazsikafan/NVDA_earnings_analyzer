# NVIDIA Earnings Analyzer - Lightweight Backend

A streamlined Flask backend for analyzing NVIDIA earnings call transcripts with AI-powered signal extraction.

## Features

- **Automatic Transcript Scraping**: Fetches NVIDIA earnings transcripts from Motley Fool
- **Management Sentiment Analysis**: Uses FinBERT to analyze executive remarks sentiment
- **Q&A Sentiment Analysis**: Analyzes tone during analyst Q&A sessions  
- **Quarter-over-Quarter Tone Changes**: Tracks sentiment trends across quarters
- **Strategic Focus Extraction**: Identifies 3-5 key themes using LLM or keyword analysis
- **Built-in Caching**: Reduces repeated processing with disk-based caching

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
```

3. **Run the server**:
```bash
python app.py
```

4. **Test the API**:
```bash
# Health check
curl http://localhost:5000/api/health

# Analyze NVIDIA earnings (last 4 quarters)
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "quarters": 4}'
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze` - Main analysis endpoint
  - Body: `{"ticker": "NVDA", "quarters": 4, "use_cache": true}`
- `GET /api/transcripts/<ticker>` - Get available transcript URLs
- `POST /api/clear-cache` - Clear analysis cache

## Architecture

The backend is designed to be lightweight and memory-efficient:

- **Lazy Loading**: Models are loaded only when needed
- **Streaming Processing**: Processes transcripts one at a time
- **Disk Caching**: Uses diskcache instead of in-memory storage
- **No Database**: Eliminates PostgreSQL/pgvector overhead
- **Minimal Dependencies**: Only essential packages included

## Deployment

### Using Gunicorn (Production)

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Using Docker

```bash
docker build -t nvda-analyzer .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key nvda-analyzer
```

### Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

## Configuration

Environment variables (in `.env`):

- `FLASK_ENV`: development/production
- `OPENAI_API_KEY`: OpenAI API key for strategic focus extraction (optional)
- `CACHE_DIR`: Directory for disk cache (default: ./cache)
- `USE_GPU`: Enable GPU for FinBERT (default: False)

## Memory Optimization

This lightweight version reduces memory usage by:

1. No PostgreSQL/pgvector - uses simple disk caching
2. No sentence embeddings - direct text analysis only
3. Lazy model loading - loads models on first use
4. Smaller transformer models - uses FinBERT instead of larger models
5. Request-based processing - no background workers

## Limitations

- No persistent storage (cache can be cleared)
- Limited to NVIDIA transcripts from Motley Fool
- Strategic focus extraction requires OpenAI API key for best results
- Single-threaded processing (use gunicorn for concurrency)

## License

MIT