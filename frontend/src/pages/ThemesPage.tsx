import React, { useState, useEffect } from 'react';
import type { ThemesResponse } from '../types';
import { getThemes } from '../services/api';
import EvidenceCard from '../components/EvidenceCard';
import EvidenceDrawer from '../components/EvidenceDrawer';

export default function ThemesPage() {
  const [themes, setThemes] = useState<ThemesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [drawerChunkId, setDrawerChunkId] = useState<string | null>(null);

  useEffect(() => {
    loadThemes(false);
  }, []);

  async function loadThemes(force: boolean) {
    if (force) setGenerating(true);
    else setLoading(true);
    try {
      const data = await getThemes(force);
      setThemes(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner" />
          <span>Loading themes...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Cross-Expert Themes</h2>
        <p className="subtitle">Recurring themes and different emphasis areas identified across all expert interviews.</p>
      </div>

      {error && <div className="error-state" style={{ marginBottom: '24px' }}>{error}</div>}

      {(!themes || themes.themes.length === 0) ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <h3 style={{ marginBottom: '8px' }}>No Themes Extracted</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Generate themes from the transcript evidence.
          </p>
          <button className="btn btn-primary" onClick={() => loadThemes(true)} disabled={generating}>
            {generating ? 'Extracting themes...' : 'Extract Themes'}
          </button>
        </div>
      ) : (
        <>
          <div className="stats-grid" style={{ marginBottom: '32px' }}>
            <div className="stat-card">
              <div className="stat-value">{themes.themes.length}</div>
              <div className="stat-label">Total Themes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{themes.common_themes}</div>
              <div className="stat-label">Common Themes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{themes.different_emphasis}</div>
              <div className="stat-label">Different Emphasis</div>
            </div>
          </div>

          <div className="themes-grid">
            {themes.themes.map((theme) => (
              <div key={theme.id} className="theme-card">
                <span className={`theme-type-badge ${theme.theme_type === 'common_theme' ? 'common' : 'emphasis'}`}>
                  {theme.theme_type === 'common_theme' ? '● Common Theme' : '◐ Different Emphasis'}
                </span>
                <h3 className="theme-name">{theme.theme_name}</h3>
                <p className="theme-description">{theme.description}</p>

                {theme.evidence.length > 0 && (
                  <div className="theme-evidence-list">
                    <div className="evidence-label">Evidence ({theme.expert_count} experts)</div>
                    {theme.evidence.map((ev, idx) => (
                      <EvidenceCard
                        key={idx}
                        source={{
                          chunk_id: ev.chunk_id,
                          country: ev.country,
                          expert_name: ev.expert_name,
                          expert_role: '',
                          timestamp: ev.timestamp,
                          quote: ev.quote,
                          verified: true,
                        }}
                        onClick={() => ev.chunk_id && setDrawerChunkId(ev.chunk_id)}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      <EvidenceDrawer chunkId={drawerChunkId} onClose={() => setDrawerChunkId(null)} />
    </div>
  );
}
