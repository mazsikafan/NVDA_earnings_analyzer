import axios from 'axios';
import { ApiResponse } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const api = {
  analyzeTranscripts: async (ticker: string = 'NVDA', quarters: number = 4): Promise<ApiResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze`, {
        ticker,
        quarters,
        use_cache: true
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  collectData: async (ticker: string = 'NVDA', quarters: number = 4): Promise<ApiResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/collect-data`, {
        ticker,
        quarters,
        use_cache: true
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  getTranscripts: async (ticker: string = 'NVDA', quarters: number = 4) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/transcripts/${ticker}`, {
        params: { quarters }
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  clearCache: async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/clear-cache`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  checkHealth: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};