import React from 'react';

interface ControlsProps {
  selectedQuarters: number;
  selectedTicker: string;
  onQuartersChange: (quarters: number) => void;
  onTickerChange: (ticker: string) => void;
  onCollectData: () => void;
  onAnalyze: () => void;
  onClearCache: () => void;
  loading: boolean;
  collectingData: boolean;
  collectMessage?: string | null;
}

const Controls: React.FC<ControlsProps> = ({
  selectedQuarters,
  selectedTicker,
  onQuartersChange,
  onTickerChange,
  onCollectData,
  onAnalyze,
  onClearCache,
  loading,
  collectingData,
  collectMessage
}) => {
  return (
    <div className="controls">
      <div className="control-group">
        <label htmlFor="ticker">Ticker:</label>
        <input
          id="ticker"
          type="text"
          value={selectedTicker}
          readOnly
          disabled={loading}
        />
      </div>
      
      <div className="control-group">
        <label htmlFor="quarters">Quarters:</label>
        <select
          id="quarters"
          value={selectedQuarters}
          onChange={(e) => onQuartersChange(Number(e.target.value))}
          disabled={loading}
        >
          <option value={1}>1 Quarter</option>
          <option value={2}>2 Quarters</option>
          <option value={3}>3 Quarters</option>
          <option value={4}>4 Quarters</option>
        </select>
      </div>
      
      <button
        className="btn btn-success"
        onClick={onCollectData}
        disabled={loading || collectingData}
      >
        {collectingData ? 'Collecting...' : 'Collect Data'}
      </button>
      
      <button
        className="btn btn-primary"
        onClick={onAnalyze}
        disabled={loading || collectingData}
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
      
      <button
        className="btn btn-secondary"
        onClick={onClearCache}
        disabled={loading || collectingData}
      >
        Clear Cache
      </button>
      
      {collectMessage && (
        <div className="collect-message">
          ✅ {collectMessage}
        </div>
      )}
    </div>
  );
};

export default Controls;