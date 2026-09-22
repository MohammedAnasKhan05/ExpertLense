import React, { useState, useEffect } from 'react';
import type { ComparisonResponse } from '../types';
import { getComparison } from '../services/api';
import EvidenceDrawer from '../components/EvidenceDrawer';

export default function ComparisonPage() {
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedCell, setExpandedCell] = useState<string | null>(null);
  const [drawerChunkId, setDrawerChunkId] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getComparison()
      .then(setComparison)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner" />
          <span>Loading comparison...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-state">{error}</div>
      </div>
    );
  }

  if (!comparison || comparison.rows.length === 0) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h2>Market Comparison</h2>
          <p className="subtitle">Run analysis first to see the comparison view.</p>
        </div>
        <div className="empty-state">
          <div className="empty-icon">⊞</div>
          <h3>No comparison data</h3>
          <p>Complete the analysis to see cross-market comparisons.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Market Comparison</h2>
        <p className="subtitle">Cross-market evidence comparison across France, Germany, and the United Kingdom.</p>
      </div>

      <div className="comparison-table-wrapper">
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Topic</th>
              {comparison.countries.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.rows.map((row) => (
              <tr key={row.topic}>
                <td>{row.topic}</td>
                {row.cells.map((cell, ci) => {
                  const cellKey = `${row.topic}-${cell.country}`;
                  const isExpanded = expandedCell === cellKey;
                  return (
                    <td
                      key={ci}
                      className="comparison-cell"
                      onClick={() => setExpandedCell(isExpanded ? null : cellKey)}
                    >
                      <div>{truncate(cell.summary, isExpanded ? 9999 : 120)}</div>
                      {isExpanded && cell.sources.length > 0 && (
                        <div style={{ marginTop: '12px' }}>
                          {cell.sources.map((src, si) => (
                            <div
                              key={si}
                              className="evidence-card"
                              style={{ marginTop: '8px', fontSize: 'var(--font-size-xs)' }}
                              onClick={(e) => { e.stopPropagation(); setDrawerChunkId(src.chunk_id); }}
                            >
                              <div className="evidence-header">
                                <span className="timestamp">{src.timestamp}</span>
                              </div>
                              <div className="evidence-quote" style={{ fontSize: 'var(--font-size-xs)' }}>
                                "{truncate(src.quote, 150)}"
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <EvidenceDrawer chunkId={drawerChunkId} onClose={() => setDrawerChunkId(null)} />
    </div>
  );
}

function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return text.slice(0, max) + '...';
}
