import React, { useState, useEffect } from 'react';
import type { AnalysisResponse } from '../types';
import { getAnalysis, runAnalysis } from '../services/api';
import EvidenceCard, { EvidenceLabel } from '../components/EvidenceCard';
import EvidenceDrawer from '../components/EvidenceDrawer';

export default function AnalysisPage() {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedQ, setExpandedQ] = useState<number | null>(null);
  const [drawerChunkId, setDrawerChunkId] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadAnalysis();
  }, []);

  async function loadAnalysis() {
    setLoading(true);
    try {
      const data = await getAnalysis();
      setAnalysis(data);
      if (data.questions.length > 0) setExpandedQ(data.questions[0].question_id);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    try {
      const data = await runAnalysis(true);
      setAnalysis(data);
      if (data.questions.length > 0) setExpandedQ(data.questions[0].question_id);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setAnalyzing(false);
    }
  }

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
          <span>Loading analysis...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Interview Analysis</h2>
        <p className="subtitle">Six questions. Three expert perspectives. One evidence trail.</p>
      </div>

      {error && <div className="error-state" style={{ marginBottom: '24px' }}>{error}</div>}

      {(!analysis || analysis.questions.length === 0) ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <h3 style={{ marginBottom: '8px' }}>No Analysis Available</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Run analysis to generate evidence-backed answers for all interview questions.
          </p>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing}>
            {analyzing ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>
      ) : (
        <div>
          {analysis.questions.map((group) => (
            <div key={group.question_id} className="question-card">
              <div
                className="question-header"
                onClick={() => setExpandedQ(expandedQ === group.question_id ? null : group.question_id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <span className="question-number">{group.question_id}</span>
                  <span className="question-text">{group.question_text}</span>
                </div>
                <span className={`question-toggle ${expandedQ === group.question_id ? 'expanded' : ''}`}>
                  ▾
                </span>
              </div>

              {expandedQ === group.question_id && (
                <div className="question-body">
                  {group.analyses.map((a) => (
                    <div key={`${a.expert_name}-${a.question_id}`} className="expert-answer">
                      <div className="expert-answer-header">
                        <span className={`country-dot ${getCountryClass(a.country)}`} />
                        <span className="expert-answer-name">{a.expert_name}</span>
                        <span className="expert-answer-role">— {a.expert_role} · {a.country}</span>
                      </div>
                      <div className="expert-answer-text">{a.answer}</div>

                      {a.sources.length > 0 && (
                        <>
                          <EvidenceLabel />
                          {a.sources.map((src, idx) => (
                            <div key={idx} style={{ marginBottom: '8px' }}>
                              <EvidenceCard
                                source={src}
                                onClick={() => setDrawerChunkId(src.chunk_id)}
                              />
                            </div>
                          ))}
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <EvidenceDrawer chunkId={drawerChunkId} onClose={() => setDrawerChunkId(null)} />
    </div>
  );
}
