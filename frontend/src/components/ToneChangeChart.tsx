import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, AreaChart, Area, ComposedChart, Cell } from 'recharts';
import { AnalysisData } from '../types';

interface ToneChangeChartProps {
  data: AnalysisData;
}

const ToneChangeChart: React.FC<ToneChangeChartProps> = ({ data }) => {
  // Create comprehensive data including all quarters and sentiment scores
  const quarterlyData = data.transcripts.map(t => ({
    quarter: `Q${t.quarter} ${t.year}`,
    managementScore: t.management_sentiment.confidence * (
      t.management_sentiment.sentiment === 'positive' ? 1 : 
      t.management_sentiment.sentiment === 'negative' ? -1 : 0
    ),
    qaScore: t.qa_sentiment.confidence * (
      t.qa_sentiment.sentiment === 'positive' ? 1 : 
      t.qa_sentiment.sentiment === 'negative' ? -1 : 0
    ),
    managementSentiment: t.management_sentiment.sentiment,
    qaSentiment: t.qa_sentiment.sentiment,
    managementConfidence: t.management_sentiment.confidence,
    qaConfidence: t.qa_sentiment.confidence
  })).reverse(); // Reverse to show chronological order

  // Prepare tone change data for change chart
  const toneData = data.tone_changes.changes.map((change, index) => ({
    period: `${change.from_quarter} → ${change.to_quarter}`,
    scoreChange: change.score_change,
    managementChange: change.management_tone_change === 'improving' ? 1 : change.management_tone_change === 'deteriorating' ? -1 : 0,
    qaChange: change.qa_tone_change === 'improving' ? 1 : change.qa_tone_change === 'deteriorating' ? -1 : 0,
    changeDetails: change
  }));

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'consistently_improving': return '📈';
      case 'consistently_deteriorating': return '📉';
      case 'generally_improving': return '↗️';
      case 'generally_deteriorating': return '↘️';
      case 'mixed': return '↔️';
      default: return '❓';
    }
  };

  const getTrendColor = (trend: string) => {
    if (trend.includes('improving')) return 'trend-positive';
    if (trend.includes('deteriorating')) return 'trend-negative';
    return 'trend-neutral';
  };

  return (
    <div className="tone-change-chart">
      <h2>Comprehensive Tone Analysis</h2>
      
      <div className="tone-summary">
        <div className={`trend-indicator ${getTrendColor(data.tone_changes.overall_trend)}`}>
          <span className="trend-icon">{getTrendIcon(data.tone_changes.overall_trend)}</span>
          <span className="trend-label">
            {data.tone_changes.overall_trend.replace(/_/g, ' ').toUpperCase()}
          </span>
        </div>
        <p className="trend-summary">{data.tone_changes.summary}</p>
      </div>

      {/* Quarterly Sentiment Progression Chart */}
      <div className="tone-chart">
        <h3>Quarterly Sentiment Progression</h3>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={quarterlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="quarter" />
            <YAxis domain={[-1, 1]} />
            <Tooltip 
              formatter={(value: number, name: string, props: any) => {
                const dataPoint = props.payload;
                if (name === 'Management Sentiment') {
                  return [`${dataPoint.managementSentiment.toUpperCase()} (${(dataPoint.managementConfidence * 100).toFixed(1)}%)`, name];
                } else if (name === 'Q&A Sentiment') {
                  return [`${dataPoint.qaSentiment.toUpperCase()} (${(dataPoint.qaConfidence * 100).toFixed(1)}%)`, name];
                }
                return [value?.toFixed(3), name];
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="managementScore" 
              stroke="#8884d8" 
              strokeWidth={3}
              name="Management Sentiment"
              dot={{ r: 6 }}
            />
            <Line 
              type="monotone" 
              dataKey="qaScore" 
              stroke="#82ca9d" 
              strokeWidth={3}
              name="Q&A Sentiment"
              dot={{ r: 6 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Quarter-over-Quarter Changes */}
      {toneData.length > 0 && (
        <div className="tone-chart">
          <h3>Quarter-over-Quarter Score Changes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={toneData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis domain={[-1, 1]} />
              <Tooltip 
                formatter={(value: number, name: string, props: any) => {
                  const change = props.payload.changeDetails;
                  if (name === 'Score Change') {
                    return [
                      `${value > 0 ? '+' : ''}${value.toFixed(3)}`,
                      `${change.overall_change.toUpperCase()} Change`
                    ];
                  }
                  return [value?.toFixed(3), name];
                }}
                labelFormatter={(label) => `Period: ${label}`}
              />
              <Legend />
              <Bar dataKey="scoreChange" name="Score Change">
                {toneData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.scoreChange > 0 ? '#10b981' : entry.scoreChange < 0 ? '#ef4444' : '#6b7280'} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {toneData.length > 0 && (
        <div className="tone-chart">
          <h3>Sentiment Confidence Levels</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={quarterlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="quarter" />
              <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
              <Tooltip 
                formatter={(value: number, name: string) => [`${(value * 100).toFixed(1)}%`, name]}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="managementConfidence" 
                stackId="1"
                stroke="#8884d8" 
                fill="#8884d8"
                fillOpacity={0.6}
                name="Management Confidence"
              />
              <Area 
                type="monotone" 
                dataKey="qaConfidence" 
                stackId="2"
                stroke="#82ca9d" 
                fill="#82ca9d"
                fillOpacity={0.6}
                name="Q&A Confidence"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="tone-details">
        <h3>Detailed Quarter-over-Quarter Changes</h3>
        <div className="change-cards">
        {data.tone_changes.changes.map((change, index) => (
          <div key={index} className="change-card">
            <h4>{change.from_quarter} → {change.to_quarter}</h4>
            <div className="change-item">
              <span className="label">Management:</span>
              <span className={`change-badge ${change.management_tone_change}`}>
                {change.management_tone_change.toUpperCase()}
              </span>
            </div>
            <div className="change-item">
              <span className="label">Q&A:</span>
              <span className={`change-badge ${change.qa_tone_change}`}>
                {change.qa_tone_change.toUpperCase()}
              </span>
            </div>
            <div className="change-item">
              <span className="label">Overall:</span>
              <span className={`change-badge ${change.overall_change}`}>
                {change.overall_change.toUpperCase()}
              </span>
            </div>
            <div className="score-change">
              Score Change: <strong>{change.score_change > 0 ? '+' : ''}{change.score_change.toFixed(3)}</strong>
            </div>
            
            {/* Enhanced LLM Analysis Section */}
            {(change.tone_shift_description || change.strategic_messaging_shift) && (
              <div className="llm-insights">
                <h5>🤖 AI-Enhanced Analysis</h5>
                
                {change.tone_shift_description && (
                  <div className="insight-item">
                    <span className="insight-label">📊 Tone Evolution:</span>
                    <p className="insight-text">{change.tone_shift_description}</p>
                  </div>
                )}
                
                {change.strategic_messaging_shift && (
                  <div className="insight-item">
                    <span className="insight-label">🎯 Strategic Messaging:</span>
                    <p className="insight-text">{change.strategic_messaging_shift}</p>
                  </div>
                )}
                
                {change.confidence_changes && (
                  <div className="insight-item">
                    <span className="insight-label">🎭 Confidence Changes:</span>
                    <p className="insight-text">{change.confidence_changes}</p>
                  </div>
                )}
                
                {change.language_style_changes && (
                  <div className="insight-item">
                    <span className="insight-label">📝 Language Style:</span>
                    <p className="insight-text">{change.language_style_changes}</p>
                  </div>
                )}
                
                {change.forward_looking_tone && (
                  <div className="insight-item">
                    <span className="insight-label">🔮 Forward Outlook:</span>
                    <p className="insight-text">{change.forward_looking_tone}</p>
                  </div>
                )}
                
                {change.key_topics_evolved && change.key_topics_evolved.length > 0 && (
                  <div className="insight-item">
                    <span className="insight-label">🔑 Evolved Topics:</span>
                    <div className="topic-tags">
                      {change.key_topics_evolved.map((topic, idx) => (
                        <span key={idx} className="topic-tag">{topic}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                {change.llm_confidence && (
                  <div className="confidence-indicator">
                    <span className="confidence-label">AI Confidence:</span>
                    <span className={`confidence-badge ${change.llm_confidence}`}>
                      {change.llm_confidence.toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        </div>
      </div>
    </div>
  );
};

export default ToneChangeChart;
