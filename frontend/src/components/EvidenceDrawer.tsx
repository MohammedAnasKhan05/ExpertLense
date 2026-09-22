import React, { useState, useEffect } from 'react';
import type { EvidenceDetail } from '../types';
import { getEvidenceDetail } from '../services/api';

interface EvidenceDrawerProps {
  chunkId: string | null;
  onClose: () => void;
}

export default function EvidenceDrawer({ chunkId, onClose }: EvidenceDrawerProps) {
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!chunkId) return;
    setLoading(true);
    setError('');
    getEvidenceDetail(chunkId)
      .then(setEvidence)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [chunkId]);

  if (!chunkId) return null;

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="evidence-drawer">
        <div className="drawer-header">
          <div>
            <span className="evidence-label">Source Evidence</span>
            <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginTop: '4px' }}>
              {evidence?.expert_name || 'Loading...'}
            </h3>
          </div>
          <button className="drawer-close" onClick={onClose}>✕</button>
        </div>
        <div className="drawer-body">
          {loading && (
            <div className="loading-container">
              <div className="spinner" />
              <span>Loading evidence...</span>
            </div>
          )}
          {error && <div className="error-state">{error}</div>}
          {evidence && !loading && (
            <>
              <div className="drawer-section">
                <div className="drawer-section-title">Expert Details</div>
                <div className="drawer-meta-grid">
                  <div className="drawer-meta-item">
                    <span className="drawer-meta-label">Name</span>
                    <span className="drawer-meta-value">{evidence.expert_name}</span>
                  </div>
                  <div className="drawer-meta-item">
                    <span className="drawer-meta-label">Role</span>
                    <span className="drawer-meta-value">{evidence.expert_role}</span>
                  </div>
                  <div className="drawer-meta-item">
                    <span className="drawer-meta-label">Country</span>
                    <span className="drawer-meta-value">{evidence.country}</span>
                  </div>
                  <div className="drawer-meta-item">
                    <span className="drawer-meta-label">Timestamp</span>
                    <span className="drawer-meta-value">{evidence.timestamp}</span>
                  </div>
                </div>
              </div>

              {evidence.context_before && (
                <div className="drawer-section">
                  <div className="drawer-section-title">Preceding Context</div>
                  <div className="drawer-transcript-context">{evidence.context_before}</div>
                </div>
              )}

              <div className="drawer-section">
                <div className="drawer-section-title">Verified Quote</div>
                <div className="drawer-verified-quote">"{evidence.quote}"</div>
              </div>

              {evidence.context_after && (
                <div className="drawer-section">
                  <div className="drawer-section-title">Following Context</div>
                  <div className="drawer-transcript-context">{evidence.context_after}</div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
