import React, { useState, useEffect } from 'react';
import { api } from './api';
import { AnalysisData } from './types';
import Header from './components/Header';
import Controls from './components/Controls';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import SentimentDashboard from './components/SentimentDashboard';
import ToneChangeChart from './components/ToneChangeChart';
import StrategicFocuses from './components/StrategicFocuses';
import TranscriptViewer from './components/TranscriptViewer';
import './App.css';

function App() {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [collectingData, setCollectingData] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedQuarters, setSelectedQuarters] = useState(4);
  const [selectedTicker, setSelectedTicker] = useState('NVDA');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'transcripts'>('dashboard');
  const [collectMessage, setCollectMessage] = useState<string | null>(null);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.analyzeTranscripts(selectedTicker, selectedQuarters);
      if (response.status === 'success' && response.data) {
        setData(response.data);
      } else {
        setError(response.message || 'Failed to fetch analysis');
      }
    } catch (err) {
      setError('Failed to connect to backend. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const collectData = async () => {
    setCollectingData(true);
    setError(null);
    setCollectMessage(null);
    try {
      const response = await api.collectData(selectedTicker, selectedQuarters);
      if (response.status === 'success') {
        setCollectMessage(response.message || 'Data collected successfully');
      } else {
        setError(response.message || 'Failed to collect data');
      }
    } catch (err) {
      setError('Failed to connect to backend. Please ensure the backend is running.');
    } finally {
      setCollectingData(false);
    }
  };

  // Remove automatic data fetching on component mount
  // useEffect(() => {
  //   fetchAnalysis();
  // }, []);

  const handleRefresh = () => {
    fetchAnalysis();
  };

  const handleClearCache = async () => {
    try {
      await api.clearCache();
      setData(null); // Clear current data
      setCollectMessage(null);
      setError(null);
    } catch (err) {
      setError('Failed to clear cache');
    }
  };

  return (
    <div className="App">
      <Header />
      
      <Controls
        selectedQuarters={selectedQuarters}
        selectedTicker={selectedTicker}
        onQuartersChange={setSelectedQuarters}
        onTickerChange={setSelectedTicker}
        onCollectData={collectData}
        onAnalyze={fetchAnalysis}
        onClearCache={handleClearCache}
        loading={loading}
        collectingData={collectingData}
        collectMessage={collectMessage}
      />

      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Analysis Dashboard
        </button>
        <button
          className={`tab-button ${activeTab === 'transcripts' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcripts')}
        >
          Transcripts
        </button>
      </div>

      <main className="main-content">
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error} onRetry={handleRefresh} />}
        
        {data && !loading && !error && (
          <>
            {activeTab === 'dashboard' ? (
              <div className="dashboard">
                <SentimentDashboard data={data} />
                <ToneChangeChart data={data} />
                <StrategicFocuses data={data} />
              </div>
            ) : (
              <TranscriptViewer data={data} />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
