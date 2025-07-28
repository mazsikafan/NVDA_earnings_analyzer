# AI Earnings Call Signal Extraction - NVIDIA Analysis

An AI-powered web application that automatically retrieves and analyzes NVIDIA's earnings call transcripts from the last four quarters, extracting key insights using advanced NLP techniques.


## Overview

This application demonstrates the power of AI in financial analysis by automatically:
- Scraping NVIDIA earnings transcripts from Motley Fool
- Segmenting transcripts into management remarks and Q&A sections
- Analyzing sentiment using FinBERT (Financial BERT)
- Tracking quarter-over-quarter tone changes
- Extracting strategic focuses using LLM analysis

## Features

### 1. **Management Sentiment Analysis**
- Uses FinBERT to analyze the sentiment of executive prepared remarks
- Provides confidence scores and detailed breakdowns
- Identifies positive, neutral, or negative tones in management communication

### 2. **Q&A Sentiment Analysis**
- Analyzes analyst questions and management responses separately
- Uses FinBERT for Q&A sentiment detection
- Modifyable to FinBERT-tone (FinBERT was found more useful for this task)

### 3. **Quarter-over-Quarter Tone Changes**
- Tracks sentiment evolution across the last 4 quarters
- Visualizes trends with interactive charts (Recharts)
- Identifies significant shifts in communication tone

### 4. **Strategic Focus Extraction**
- Extracts 3-5 key themes per quarter using AI
- Supported by OpenAI GPT-4 
- Tracks evolving priorities (AI growth, data center expansion, etc.)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React App     │────▶│   Flask API     │────▶│  Motley Fool    │
│   (Frontend)    │     │   (Backend)     │     │   (Scraper)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   AI Models     │
                        │ - FinBERT       │
                        │ - OpenAI GPT    │
                        └─────────────────┘
```

### Frontend (React + TypeScript) 
- **Implementation**: 100% implemented with Github Copilot, the visualization is based on own ideas.
- **Framework**: React 19 with TypeScript
- **UI Components**: Custom components for sentiment dashboards, charts, and transcript viewer
- **Data Visualization**: Recharts for interactive charts
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Axios for backend communication

### Backend (Flask)
- **Framework**: Lightweight Flask with CORS support
- **Caching**: DiskCache for 1-hour result caching (SQLite-based)
- **Models**: Lazy-loaded transformers for memory efficiency
- **Architecture**: RESTful API with JSON responses

## 🛠️ Tech Stack

### AI/NLP Tools
- **FinBERT** (ProsusAI/finbert): Financial sentiment analysis and Q&A tone detection
- **OpenAI GPT-4**: Strategic focus extraction
- **Transformers**: Hugging Face transformers library
- **PyTorch**: Deep learning framework

### Web Technologies
- **Frontend**: React, TypeScript, Recharts, Axios
- **Backend**: Flask, Flask-CORS, Gunicorn
- **Scraping**: BeautifulSoup4, Requests
- **Caching**: DiskCache (SQLite-based)

## Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/earnings_analyzer.git
cd earnings_analyzer
```

2. **Backend Setup**
```bash
cd backend_lite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional)

# Run the backend
python app.py
```

3. **Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📡 API Documentation

### Endpoints

#### `GET /api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00"
}
```

#### `POST /api/analyze`
Main analysis endpoint
```json
// Request
{
  "ticker": "NVDA",
  "quarters": 4,
  "use_cache": true
}

// Response
{
  "status": "success",
  "data": {
    "quarters": [...],
    "overall_sentiment": {...},
    "tone_changes": {...},
    "strategic_focuses": [...]
  }
}
```

#### `GET /api/transcripts/<ticker>`
Get available transcript URLs

#### `POST /api/clear-cache`
Clear the analysis cache

## 💻 Usage Examples

### Analyzing Earnings
1. Click "Analyze NVDA Earnings" button
2. Wait for data collection and processing
3. View results in the Analysis Dashboard tab

### Viewing Transcripts
1. Switch to "Transcripts" tab
2. Select quarter from dropdown
3. Toggle between full text and segmented view

### Understanding Sentiment Scores
- **Positive**: Score > 0.6 (Green)
- **Neutral**: 0.4 ≤ Score ≤ 0.6 (Yellow)
- **Negative**: Score < 0.4 (Red)

## 📝 Key Assumptions & Limitations

### Assumptions
- **Main Assumption**: Sentiment and strategic insights can be derived from earnings call transcripts
- **Data Source**: Relies on Motley Fool's transcript formatting
- **Ticker Focus**: Currently hardcoded for NVIDIA (NVDA)
- **Time Period**: Analyzes only the most recent 4 quarters available
- **Large Language Models**: LLMS can hallucinate, with proper fine tuning, the results can be significantly improved. For better results, using chain-of-thought reasoning is beneficial.

### Limitations
- **Rate Limiting**: Motley Fool may rate-limit scraping requests
- **Model Size**: FinBERT models require ~2GB memory when loaded
- **Strategic Analysis**: Best results with OpenAI API key; fallback uses keyword extraction
- **Historical Data**: Limited to transcripts available on Motley Fool
- **Processing Time**: Initial analysis could be asynchronous.

### Design Decisions
- **No Database**: Uses file-based caching to reduce complexity
- **Lazy Loading**: Models loaded on-demand to optimize memory
- **Segmentation**: Simple pattern matching for transcript parsing (!) May fail if extending to other companies
- **Cache Duration**: 1-hour cache to balance freshness and performance

## 📄 License

MIT License - feel free to use this code for your own projects!

---

Built using React, Flask, and state-of-the-art NLP models.
