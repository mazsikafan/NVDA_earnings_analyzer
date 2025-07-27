## AI Earnings Call Signal Extraction v3
## Objective
build an AI-powered application that identifies, retrieves, and analyzes the earnings call transcripts for NVIDIA over the last four quarters. The application should extract key insights using natural language processing techniques and surface four types of signals:
- Management Sentiment
- Q&A Sentiment
- Quarter-over-Quarter Tone Change
- Strategic Focuses
## Deliverables
1. A GitHub repository with your source code and a clear README file.
2. A live link to the deployed application (on Vercel or any platform of your choice).
Requirements
1. Data Module
- Automatically identify and retrieve full transcripts of NVIDIA’s earnings calls for the
last four quarters.
- use a scraper that scrapes the raw Montley Fool's earnings call transcripts from the web.
- use a parser to segment the transcripts into:
  - Management Prepared Remarks
  - Q&A Session 
2. Signal Extraction
Implement  AI-powered logic to extract the following from each transcript:
- Management Sentiment: Overall sentiment (positive/neutral/negative) of prepared
remarks by executives. - FinBert
- Q&A Sentiment: Overall tone and sentiment during the Q&A portion. - finbert-tone
- Quarter-over-Quarter Tone Change: Analyze and compare sentiment/tone shifts
across the four quarters. -
- Strategic Focuses: Extract 3–5 key themes or initiatives emphasized each quarter
(e.g., AI growth, data center expansion).
3. User Interface
Provide a web-based interface to:
- Display the transcripts.
- Visualize sentiment scores (e.g., with charts).
- Highlight major strategic focuses.
- Show tone change trends across quarters.
4. Deployment
- Deploy the application on Vercel platform.
- Ensure the site is accessible, responsive, and loads key features quickly.
5. README & Documentation
Include a README.md with:
- What the app does
- How to run it locally
- Any AI/NLP tools, APIs, or models used
- Key assumptions or limitations
6. Guidelines
- You may use Google Gemini, ChatGPT, Cursor, Windsurf, LangChain, or any modern AI/NLP tools.
- Prefer using LLMs or embeddings-based approaches for analyzing tone and
extracting key topics.
- Focus on building something functional and insightful, even if rough around the
edges.
- Explain any shortcuts or manual steps taken due to time constraints.
## Evaluation Criteria
Category -  Description
Functionality - Does the app complete the tasks: fetching transcripts, extracting
insights, and displaying them clearly?
Code Quality - Is the codebase readable, maintainable, and logically structured?
Use of AI Tools - How effectively were LLMs or NLP libraries used to extract
insights?
UI/UX - Is the app intuitive, clean, and informative?
Deployment - Is the app publicly accessible and working as expected?
# Project Directory Structure

```
earnings_analyzer/
├── CLAUDE.md                           # Project specifications and instructions
├── README.md                           # Main project documentation
├── .git/                               # Git repository
├── .claude/                            # Claude configuration
│
└── backend_lite/                       # Lightweight Flask backend
    ├── README.md                       # Backend documentation
    ├── requirements.txt                # Minimal Python dependencies
    ├── .env                            # Environment configuration (with API keys)
    ├── .env.example                    # Example environment configuration
    ├── .gitignore                      # Git ignore file
    ├── app.py                          # Main Flask application with all routes
    ├── Dockerfile                      # Docker container definition
    ├── Procfile                        # Heroku deployment configuration
    ├── vercel.json                     # Vercel deployment configuration
    ├── debug_scraper.py                # Scraper debugging utility
    ├── generate_report.py              # Generate formatted analysis report
    │
    ├── services/                       # Core service modules
    │   ├── __init__.py                 # Services package init
    │   ├── scraper.py                  # Motley Fool transcript scraper
    │   ├── parser.py                   # Transcript parser (management/Q&A segmentation)
    │   ├── sentiment_analyzer.py       # FinBERT & FinBERT-tone sentiment analysis
    │   ├── tone_analyzer.py            # Quarter-over-quarter tone change analysis
    │   └── strategic_analyzer.py       # Strategic focuses extraction (LLM/keyword-based)
    │
    ├── tests/                          # Test scripts
    │   ├── test_api.py                 # API endpoint testing
    │   └── test_segmentation.py        # Transcript segmentation verification
    │
    ├── scripts/                        # Utility scripts
    │   ├── show_data_format.py         # Display data storage formats
    │   └── inspect_cache.py            # Inspect cache contents
    │
    └── cache/                          # DiskCache storage (auto-generated)
        ├── cache.db                    # SQLite cache database
        ├── cache.db-shm                # SQLite shared memory
        └── cache.db-wal                # SQLite write-ahead log
```