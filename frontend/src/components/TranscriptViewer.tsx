import React, { useState } from 'react';
import { AnalysisData } from '../types';

interface TranscriptViewerProps {
  data: AnalysisData;
}

const TranscriptViewer: React.FC<TranscriptViewerProps> = ({ data }) => {
  const [selectedQuarter, setSelectedQuarter] = useState(0);

  const transcript = data.transcripts[selectedQuarter];

  return (
    <div className="transcript-viewer">
      <h2>Earnings Call Transcripts</h2>
      
      <div className="transcript-selector">
        <label>Select Quarter:</label>
        <select 
          value={selectedQuarter} 
          onChange={(e) => setSelectedQuarter(Number(e.target.value))}
        >
          {data.transcripts.map((t, index) => (
            <option key={index} value={index}>
              Q{t.quarter} {t.year}
            </option>
          ))}
        </select>
      </div>

      <div className="transcript-content">
        <div className="transcript-header">
          <h3>Q{transcript.quarter} {transcript.year} Earnings Call</h3>
          <a 
            href={transcript.transcript_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="transcript-link"
          >
            View Original Transcript →
          </a>
        </div>

        <div className="transcript-stats">
          <div className="stat-card">
            <h4>Management Remarks</h4>
            <div className="stat-value">{transcript.prepared_remarks_count} segments</div>
            <div className={`sentiment-indicator ${transcript.management_sentiment.sentiment}`}>
              {transcript.management_sentiment.sentiment.toUpperCase()}
              <span className="confidence">
                ({(transcript.management_sentiment.confidence * 100).toFixed(1)}%)
              </span>
            </div>
          </div>
          
          <div className="stat-card">
            <h4>Q&A Session</h4>
            <div className="stat-value">{transcript.qa_count} exchanges</div>
            <div className={`sentiment-indicator ${transcript.qa_sentiment.sentiment}`}>
              {transcript.qa_sentiment.sentiment.toUpperCase()}
              <span className="confidence">
                ({(transcript.qa_sentiment.confidence * 100).toFixed(1)}%)
              </span>
            </div>
          </div>
        </div>

        <div className="transcript-sentiment-breakdown">
          <h4>Sentiment Score Breakdown</h4>
          <div className="sentiment-scores">
            <div className="score-section">
              <h5>Management Sentiment</h5>
              <div className="score-bars">
                <div className="score-bar">
                  <span className="score-label">Positive</span>
                  <div className="bar-container">
                    <div 
                      className="bar positive" 
                      style={{ width: `${transcript.management_sentiment.scores.positive * 100}%` }}
                    />
                  </div>
                  <span className="score-value">
                    {(transcript.management_sentiment.scores.positive * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="score-bar">
                  <span className="score-label">Neutral</span>
                  <div className="bar-container">
                    <div 
                      className="bar neutral" 
                      style={{ width: `${transcript.management_sentiment.scores.neutral * 100}%` }}
                    />
                  </div>
                  <span className="score-value">
                    {(transcript.management_sentiment.scores.neutral * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="score-bar">
                  <span className="score-label">Negative</span>
                  <div className="bar-container">
                    <div 
                      className="bar negative" 
                      style={{ width: `${transcript.management_sentiment.scores.negative * 100}%` }}
                    />
                  </div>
                  <span className="score-value">
                    {(transcript.management_sentiment.scores.negative * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
            
            <div className="score-section">
              <h5>Q&A Sentiment</h5>
              <div className="score-bars">
                <div className="score-bar">
                  <span className="score-label">Positive</span>
                  <div className="bar-container">
                    <div 
                      className="bar positive" 
                      style={{ width: `${transcript.qa_sentiment.scores.positive * 100}%` }}
                    />
                  </div>
                  <span className="score-value">
                    {(transcript.qa_sentiment.scores.positive * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="score-bar">
                  <span className="score-label">Neutral</span>
                  <div className="bar-container">
                    <div 
                      className="bar neutral" 
                      style={{ width: `${transcript.qa_sentiment.scores.neutral * 100}%` }}
                    />
                  </div>
                  <span className="score-value">
                    {(transcript.qa_sentiment.scores.neutral * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="score-bar">
                  <span className="score-label">Negative</span>
                  <div className="bar-container">
                    <div 
                      className="bar negative" 
                      style={{ width: `${transcript.qa_sentiment.scores.negative * 100}%` }}
                    />
                  </div>
                  <span className="score-value">
                    {(transcript.qa_sentiment.scores.negative * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="transcript-notice">
          <p>
            📄 Full transcript text is available at the source. Click the link above to read the complete earnings call transcript.
          </p>
        </div>
      </div>
    </div>
  );
};

export default TranscriptViewer;