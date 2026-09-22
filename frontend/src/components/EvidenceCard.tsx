import React from 'react';
import type { Source } from '../types';

interface EvidenceCardProps {
  source: Source;
  onClick?: () => void;
}

export default function EvidenceCard({ source, onClick }: EvidenceCardProps) {
  return (
    <div className="evidence-card" onClick={onClick}>
      <div className="evidence-header">
        <span className="expert-name">{source.expert_name}</span>
        <span className="separator">—</span>
        <span className="country-badge">{source.country}</span>
        <span className="timestamp">{source.timestamp}</span>
      </div>
      <div className="evidence-quote">"{source.quote}"</div>
    </div>
  );
}


export function EvidenceLabel() {
  return <div className="evidence-label">Evidence</div>;
}
