import React, { useState, useEffect } from 'react';
import type { DocumentSchema, AnalysisResponse, HealthResponse } from '../types';
import { getTranscripts, getAnalysis, getHealth, seedTranscripts, runAnalysis } from '../services/api';

export default function OverviewPage() {
  const [docs, setDocs] = useState<DocumentSchema[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [h, d] = await Promise.all([getHealth(), getTranscripts()]);
      setHealth(h);
      setDocs(d);
      if (d.length > 0) {
        try { const a = await getAnalysis(); setAnalysis(a); } catch {}
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSeed() {
    setSeeding(true);
    try {
      await seedTranscripts();
      await loadData();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSeeding(false);
    }
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    try {
      const a = await runAnalysis(true);
      setAnalysis(a);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setAnalyzing(false);
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getCountryClass = (country: string) => {
    if (country.toLowerCase().includes('france')) return 'france';
    if (country.toLowerCase().includes('germany')) return 'germany';
    return 'uk';
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner" />
          <span>Loading ExpertLens AI...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <p className="subtitle" style={{ marginBottom: '4px' }}>{getGreeting()}</p>
        <h2>Expert interview intelligence<br/>for European robotic surgery.</h2>
      </div>

      {error && <div className="error-state" style={{ marginBottom: '24px' }}>{error}</div>}

      {docs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <h3 style={{ marginBottom: '8px' }}>Get Started</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Seed the database with the three expert interview transcripts to begin analysis.
          </p>
          <button className="btn btn-primary" onClick={handleSeed} disabled={seeding}>
            {seeding ? 'Seeding...' : 'Seed Demo Transcripts'}
          </button>
        </div>
      ) : (
        <>
          {/* Stats */}
          <div className="stats-grid" style={{ marginBottom: '32px' }}>
            <div className="stat-card">
              <div className="stat-value">{docs.length}</div>
              <div className="stat-label">Experts</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{new Set(docs.map(d => d.country)).size}</div>
              <div className="stat-label">Markets</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">6</div>
              <div className="stat-label">Questions</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{analysis?.total_evidence || '—'}</div>
              <div className="stat-label">Evidence Points</div>
            </div>
          </div>

          {/* Actions */}
          {!analysis?.total_evidence && (
            <div className="card" style={{ textAlign: 'center', padding: '32px', marginBottom: '32px' }}>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
                Transcripts loaded. Run analysis to generate evidence-backed intelligence.
              </p>
              <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing}>
                {analyzing ? 'Analyzing transcripts...' : 'Run Analysis'}
              </button>
            </div>
          )}

          {/* Evidence badge */}
          {analysis && analysis.total_evidence > 0 && (
            <div style={{ marginBottom: '32px' }}>
              <span className="grounded-badge">✓ Evidence grounded — 100% source traceable</span>
              {health && (
                <span className="provider-badge" style={{ marginLeft: '12px' }}>
                  {health.llm_provider}
                </span>
              )}
            </div>
          )}

          {/* Market Cards */}
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '16px' }}>Markets</h3>
          <div className="market-cards">
            {docs.map((doc) => (
              <div key={doc.id} className={`market-card ${getCountryClass(doc.country)}`}>
                <div className="country-name">{doc.country}</div>
                <div className="expert-info">
                  {doc.expert_name}<br/>
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-tertiary)' }}>
                    {doc.expert_role}
                  </span>
                </div>
                <div className="market-details">
                  <div className="market-detail-item">
                    <span className="detail-label">Transcript</span>
                    <span className="detail-value">{doc.chunk_count} segments</span>
                  </div>
                  <div className="market-detail-item">
                    <span className="detail-label">Status</span>
                    <span className="detail-value" style={{ color: 'var(--success)' }}>Indexed</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
