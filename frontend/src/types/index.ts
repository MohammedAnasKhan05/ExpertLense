/* Types */

export interface DocumentSchema {
  id: string;
  filename: string;
  expert_name: string;
  expert_role: string;
  country: string;
  created_at: string;
  chunk_count: number;
}

export interface TranscriptChunkSchema {
  id: string;
  document_id: string;
  timestamp: string;
  speaker: string;
  text: string;
  chunk_index: number;
}

export interface DocumentDetailSchema extends DocumentSchema {
  chunks: TranscriptChunkSchema[];
  raw_text: string;
}

export interface Source {
  chunk_id: string;
  country: string;
  expert_name: string;
  expert_role: string;
  timestamp: string;
  quote: string;
  verified: boolean;
}

export interface QuestionAnalysis {
  question_id: number;
  question_text: string;
  expert_name: string;
  expert_role: string;
  country: string;
  answer: string;
  sources: Source[];
  confidence: string;
}

export interface QuestionAnalysisGroup {
  question_id: number;
  question_text: string;
  analyses: QuestionAnalysis[];
}

export interface AnalysisResponse {
  questions: QuestionAnalysisGroup[];
  total_questions: number;
  total_experts: number;
  total_evidence: number;
}

export interface ComparisonCell {
  country: string;
  expert_name: string;
  expert_role: string;
  summary: string;
  sources: Source[];
}

export interface ComparisonRow {
  topic: string;
  cells: ComparisonCell[];
}

export interface ComparisonResponse {
  rows: ComparisonRow[];
  countries: string[];
}

export interface ThemeEvidence {
  chunk_id: string;
  expert_name: string;
  country: string;
  quote: string;
  timestamp: string;
}

export interface Theme {
  id: string;
  theme_name: string;
  description: string;
  theme_type: string;
  evidence: ThemeEvidence[];
  expert_count: number;
}

export interface ThemesResponse {
  themes: Theme[];
  common_themes: number;
  different_emphasis: number;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  confidence: string;
  suggested_questions: string[];
}

export interface EvidenceDetail {
  chunk_id: string;
  expert_name: string;
  expert_role: string;
  country: string;
  timestamp: string;
  quote: string;
  context_before: string;
  context_after: string;
  full_text: string;
  document_id: string;
  verified: boolean;
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  llm_provider: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  confidence?: string;
}
