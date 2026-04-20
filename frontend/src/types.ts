export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface LLMOption {
  name: string;
  value: string;
}

export interface TimeStats {
  video_length_seconds: number;
  video_length_minutes: number;
  word_count: number;
  reading_time_seconds: number;
  reading_time_minutes: number;
  time_saved_seconds: number;
  time_saved_minutes: number;
  percentage_saved: number;
}

export interface SummaryResult {
  video_title: string;
  video_url: string;
  llm_used: string;
  language: string;
  transcript: string;
  summary: string;
  time_stats: TimeStats;
}
