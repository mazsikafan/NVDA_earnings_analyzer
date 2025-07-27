import React from 'react';
import { AnalysisData } from '../types';

interface StrategicFocusesProps {
  data: AnalysisData;
}

const StrategicFocuses: React.FC<StrategicFocusesProps> = ({ data }) => {
  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high': return 'importance-high';
      case 'medium': return 'importance-medium';
      case 'low': return 'importance-low';
      default: return '';
    }
  };

  const getImportanceIcon = (importance: string) => {
    switch (importance) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '';
    }
  };

  // Aggregate themes across quarters
  const themeFrequency: { [key: string]: number } = {};
  data.strategic_focuses.forEach(qf => {
    qf.focuses.forEach(focus => {
      themeFrequency[focus.title] = (themeFrequency[focus.title] || 0) + 1;
    });
  });

  const topThemes = Object.entries(themeFrequency)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="strategic-focuses">
      <h2>Strategic Focuses</h2>
      
      <div className="themes-overview">
        <h3>Top Strategic Themes Across All Quarters</h3>
        <div className="theme-tags">
          {topThemes.map(([theme, count]) => (
            <div key={theme} className="theme-tag">
              <span className="theme-name">{theme}</span>
              <span className="theme-count">{count}Q</span>
            </div>
          ))}
        </div>
      </div>

      <div className="quarterly-focuses">
        <h3>Quarterly Strategic Focuses</h3>
        {data.strategic_focuses.map((quarterFocus, index) => (
          <div key={index} className="quarter-focus">
            <h4>Q{quarterFocus.quarter} {quarterFocus.year}</h4>
            <div className="focus-list">
              {quarterFocus.focuses.map((focus, fIndex) => (
                <div key={fIndex} className={`focus-item ${getImportanceColor(focus.importance)}`}>
                  <div className="focus-header">
                    <span className="importance-icon">{getImportanceIcon(focus.importance)}</span>
                    <h5>{focus.title}</h5>
                    <span className="importance-badge">{focus.importance.toUpperCase()}</span>
                  </div>
                  <p className="focus-description">{focus.description}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StrategicFocuses;