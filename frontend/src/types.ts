// Type definitions for the earnings analyzer

export interface TranscriptData {
  quarter: number;
  year: number;
  transcript_url: string;
  management_sentiment: SentimentData;
  qa_sentiment: SentimentData;
  prepared_remarks_count: number;
  qa_count: number;
}

export interface SentimentData {
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  scores: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export interface ToneChange {
  from_quarter: string;
  to_quarter: string;
  management_tone_change: string;
  qa_tone_change: string;
  overall_change: string;
  score_change: number;
  // Enhanced LLM Analysis fields
  tone_shift_description?: string;
  confidence_changes?: string;
  key_topics_evolved?: string[];
  strategic_messaging_shift?: string;
  language_style_changes?: string;
  forward_looking_tone?: string;
  llm_confidence?: string;
  // Legacy field for compatibility
  llm_analysis?: string;
}

export interface ToneChangesData {
  overall_trend: string;
  summary: string;
  changes: ToneChange[];
}

export interface StrategicFocus {
  title: string;
  description: string;
  importance: 'high' | 'medium' | 'low';
}

export interface QuarterlyFocus {
  quarter: number;
  year: number;
  focuses: StrategicFocus[];
}

export interface AnalysisData {
  ticker: string;
  quarters_analyzed: number;
  transcripts: TranscriptData[];
  tone_changes: ToneChangesData;
  strategic_focuses: QuarterlyFocus[];
  analysis_timestamp: string;
}

export interface ApiResponse {
  status: 'success' | 'error';
  data?: AnalysisData;
  message?: string;
  from_cache?: boolean;
}