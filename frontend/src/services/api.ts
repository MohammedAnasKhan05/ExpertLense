/**
 * ExpertLens AI — API Client
 * 
 * Typed API client for all backend endpoints.
 */

import type {
  HealthResponse,
  DocumentSchema,
  DocumentDetailSchema,
  AnalysisResponse,
  ComparisonResponse,
  ThemesResponse,
  ChatResponse,
  EvidenceDetail,
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }
  return response.json();
}

// Health
export async function getHealth(): Promise<HealthResponse> {
  return fetchJSON('/health');
}

// Transcripts
export async function getTranscripts(): Promise<DocumentSchema[]> {
  return fetchJSON('/api/transcripts');
}

export async function getTranscript(id: string): Promise<DocumentDetailSchema> {
  return fetchJSON(`/api/transcripts/${id}`);
}

export async function seedTranscripts(): Promise<{ results: any[]; total: number }> {
  return fetchJSON('/api/transcripts/seed', { method: 'POST' });
}

export async function uploadTranscriptFile(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/api/transcripts/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Upload Error: ${response.status}`);
  }
  return response.json();
}

export async function createTranscriptText(data: {
  expert_name: string;
  expert_role: string;
  country: string;
  raw_text: string;
  filename?: string;
}): Promise<any> {
  return fetchJSON('/api/transcripts/create', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Analysis
export async function runAnalysis(forceRegenerate = false): Promise<AnalysisResponse> {
  return fetchJSON('/api/analysis/analyze', {
    method: 'POST',
    body: JSON.stringify({ force_regenerate: forceRegenerate }),
  });
}

export async function getAnalysis(): Promise<AnalysisResponse> {
  return fetchJSON('/api/analysis/questions');
}

export async function getComparison(): Promise<ComparisonResponse> {
  return fetchJSON('/api/analysis/comparison');
}

export async function getThemes(force = false): Promise<ThemesResponse> {
  return fetchJSON(`/api/analysis/themes?force=${force}`);
}

// Chat
export async function sendChatMessage(
  question: string,
  countryFilter?: string,
  expertFilter?: string,
): Promise<ChatResponse> {
  return fetchJSON('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      question,
      country_filter: countryFilter || null,
      expert_filter: expertFilter || null,
    }),
  });
}

// Evidence
export async function getEvidenceDetail(chunkId: string): Promise<EvidenceDetail> {
  return fetchJSON(`/api/evidence/${chunkId}`);
}
