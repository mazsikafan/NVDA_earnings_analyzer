# NVIDIA Earnings Analyzer Frontend

A lightweight React frontend for visualizing AI-powered earnings call analysis.

## Features

- 📊 **Sentiment Visualization**: Interactive charts showing management and Q&A sentiment
- 📈 **Tone Change Trends**: Quarter-over-quarter sentiment tracking
- 🎯 **Strategic Focus Display**: Key themes and initiatives highlighted
- 📄 **Transcript Viewer**: Easy access to earnings call details
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js 14+ and npm
- Backend API running (see backend_lite README)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your backend URL:
```
REACT_APP_API_URL=http://localhost:5000
```

### Development

Run the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000).

### Production Build

Build for production:
```bash
npm run build
```

## Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variable in Vercel dashboard:
   - `REACT_APP_API_URL`: Your deployed backend URL

### Deploy with GitHub

1. Push to GitHub
2. Connect repository to Vercel
3. Configure environment variables
4. Deploy automatically on push

## Configuration

### Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:5000)

### Vercel Configuration

The `vercel.json` file configures:
- API proxy rewrites
- Security headers
- Build settings

## UI Components

### Analysis Dashboard
- **Sentiment Dashboard**: Pie charts and timeline visualization
- **Tone Change Chart**: Line chart showing sentiment progression
- **Strategic Focuses**: Categorized key themes by importance

### Transcript Viewer
- Quarter selector
- Sentiment score breakdown
- Link to original transcript
- Segment statistics

## Technology Stack

- **React** with TypeScript
- **Recharts** for data visualization
- **Axios** for API calls
- **CSS** for styling (no heavy UI frameworks)

## API Integration

The frontend connects to the backend API endpoints:
- `POST /api/analyze`: Fetch earnings analysis
- `GET /api/transcripts/:ticker`: Get available transcripts
- `POST /api/clear-cache`: Clear analysis cache
- `GET /api/health`: Check backend status

## License

MIT
