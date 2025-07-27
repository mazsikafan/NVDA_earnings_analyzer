import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AnalysisData } from '../types';

interface SentimentDashboardProps {
  data: AnalysisData;
}

const SentimentDashboard: React.FC<SentimentDashboardProps> = ({ data }) => {
  // Prepare data for sentiment charts - using a clearer scale
  const getSentimentScore = (sentiment: string, confidence: number) => {
    switch (sentiment) {
      case 'positive': return confidence;
      case 'negative': return -confidence;
      case 'neutral': return 0; // Keep neutral at 0 but show all data points
      default: return 0;
    }
  };

  const sentimentData = data.transcripts.map(t => ({
    quarter: `Q${t.quarter} ${t.year}`,
    management: getSentimentScore(t.management_sentiment.sentiment, t.management_sentiment.confidence),
    qa: getSentimentScore(t.qa_sentiment.sentiment, t.qa_sentiment.confidence),
    managementLabel: t.management_sentiment.sentiment,
    qaLabel: t.qa_sentiment.sentiment
  }));

  // Aggregate sentiment distribution
  const sentimentCounts = {
    management: { positive: 0, neutral: 0, negative: 0 },
    qa: { positive: 0, neutral: 0, negative: 0 }
  };

  data.transcripts.forEach(t => {
    sentimentCounts.management[t.management_sentiment.sentiment]++;
    sentimentCounts.qa[t.qa_sentiment.sentiment]++;
  });

  const pieData = {
    management: [
      { name: 'Positive', value: sentimentCounts.management.positive, color: '#10b981' },
      { name: 'Neutral', value: sentimentCounts.management.neutral, color: '#6b7280' },
      { name: 'Negative', value: sentimentCounts.management.negative, color: '#ef4444' }
    ],
    qa: [
      { name: 'Positive', value: sentimentCounts.qa.positive, color: '#10b981' },
      { name: 'Neutral', value: sentimentCounts.qa.neutral, color: '#6b7280' },
      { name: 'Negative', value: sentimentCounts.qa.negative, color: '#ef4444' }
    ]
  };

  return (
    <div className="sentiment-dashboard">
      <h2>Sentiment Analysis Dashboard</h2>
      
      <div className="sentiment-overview">
        <div className="sentiment-pie-charts">
          <div className="pie-chart-container">
            <h3>Management Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData.management.filter(d => d.value > 0)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.management.filter(d => d.value > 0).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="pie-chart-container">
            <h3>Q&A Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData.qa.filter(d => d.value > 0)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.qa.filter(d => d.value > 0).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="sentiment-timeline">
          <h3>Sentiment Timeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sentimentData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="quarter" />
              <YAxis domain={[-1, 1]} tickCount={5} />
              <Tooltip 
                formatter={(value: number, name: string, props: any) => {
                  const dataPoint = props.payload;
                  const label = name === 'Management' ? dataPoint.managementLabel : dataPoint.qaLabel;
                  const confidence = Math.abs(value);
                  const sentiment = label?.toUpperCase() || 'UNKNOWN';
                  return [`${sentiment} (${(confidence * 100).toFixed(1)}%)`, name];
                }}
              />
              <Legend />
              <Bar dataKey="management" fill="#8884d8" name="Management" minPointSize={5} />
              <Bar dataKey="qa" fill="#82ca9d" name="Q&A" minPointSize={5} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="sentiment-details">
        <h3>Quarterly Sentiment Details</h3>
        <div className="sentiment-cards">
          {data.transcripts.map((transcript, index) => (
            <div key={index} className="sentiment-card">
              <h4>Q{transcript.quarter} {transcript.year}</h4>
              <div className="sentiment-item">
                <span className="label">Management:</span>
                <span className={`sentiment-badge ${transcript.management_sentiment.sentiment}`}>
                  {transcript.management_sentiment.sentiment.toUpperCase()}
                </span>
                <span className="confidence">
                  ({(transcript.management_sentiment.confidence * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="sentiment-item">
                <span className="label">Q&A:</span>
                <span className={`sentiment-badge ${transcript.qa_sentiment.sentiment}`}>
                  {transcript.qa_sentiment.sentiment.toUpperCase()}
                </span>
                <span className="confidence">
                  ({(transcript.qa_sentiment.confidence * 100).toFixed(1)}%)
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SentimentDashboard;