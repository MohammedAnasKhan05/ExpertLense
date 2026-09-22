import React, { useState, useRef, useEffect } from 'react';
import type { ChatMessage } from '../types';
import { sendChatMessage } from '../services/api';
import EvidenceCard from '../components/EvidenceCard';
import EvidenceDrawer from '../components/EvidenceDrawer';

const SUGGESTED = [
  'What are the biggest barriers to robotic surgery adoption?',
  'How important is ROI to hospital purchasing decisions?',
  'How does the UK perspective differ from Germany?',
  'What do experts say about surgeon training?',
  'What is the expected adoption trend over the next 3–5 years?',
  'How long does a typical purchasing decision take?',
];

function renderFormattedContent(content: string) {
  const lines = content.split('\n');
  return (
    <div className="formatted-message" style={{ lineHeight: 1.65, color: '#111827' }}>
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={idx} style={{ height: '8px' }} />;
        }

        // Section headings (### 1. Synthesized Analysis, ### 2. Transcript Evidence & References)
        if (trimmed.startsWith('### ') || trimmed.startsWith('## ') || trimmed.startsWith('# ')) {
          return (
            <h4 key={idx} style={{
              fontSize: '1.05rem',
              fontWeight: 700,
              color: 'var(--color-primary, #2563eb)',
              marginTop: idx === 0 ? 0 : '16px',
              marginBottom: '8px',
              borderBottom: '1px solid #e2e8f0',
              paddingBottom: '4px',
            }}>
              {trimmed.replace(/^#+\s*/, '')}
            </h4>
          );
        }

        // Bullet point with bold prefix: - **United Kingdom**: ... or - **Dr. Jean Martin (France, 00:18)**: ...
        if (trimmed.startsWith('- **') || trimmed.startsWith('**')) {
          const match = trimmed.match(/^(?:-\s*)?\*\*(.+?)\*\*:\s*(.*)$/);
          if (match) {
            return (
              <div key={idx} style={{ margin: '6px 0 6px 8px', fontSize: '0.95rem', color: '#111827' }}>
                <strong style={{ color: '#000000', fontWeight: 700 }}>{match[1]}:</strong>{' '}
                <span style={{ color: '#111827', fontWeight: 400 }}>{match[2]}</span>
              </div>
            );
          }
        }

        // Speaker citation pattern: Dr. Jean Martin (France, 00:18): "..." or [00:18] Speaker: ...
        const speakerMatch = trimmed.match(/^([A-Za-z0-9.\s]+(?:\([^)]+\))?):\s*(.*)$/);
        if (speakerMatch && (trimmed.includes('(') || trimmed.includes(': "') || trimmed.includes('Dr.') || trimmed.includes('Interviewer'))) {
          return (
            <div key={idx} style={{ margin: '6px 0 6px 8px', fontSize: '0.95rem', color: '#111827' }}>
              <strong style={{ color: '#000000', fontWeight: 700 }}>{speakerMatch[1]}:</strong>{' '}
              <span style={{ color: '#111827', fontWeight: 400 }}>{speakerMatch[2]}</span>
            </div>
          );
        }

        // Regular bullet list item
        if (trimmed.startsWith('- ')) {
          return (
            <div key={idx} style={{ margin: '4px 0 4px 12px', fontSize: '0.95rem', color: '#111827' }}>
              • {trimmed.slice(2)}
            </div>
          );
        }

        // Default paragraph
        return (
          <p key={idx} style={{ margin: '4px 0', fontSize: '0.95rem', color: '#111827', fontWeight: 400 }}>
            {trimmed}
          </p>
        );
      })}
    </div>
  );
}

export default function ResearchPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [drawerChunkId, setDrawerChunkId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend(question?: string) {
    const q = (question || input).trim();
    if (!q || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(q);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `Error: ${e.message}. Please ensure the backend is running.`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="page-container">
      <div className="chat-container">
        {messages.length === 0 && (
          <div className="chat-header-section">
            <h2>Ask the interviews.</h2>
            <p>Get evidence-backed answers across all expert conversations.</p>
            <div className="suggested-questions" style={{ justifyContent: 'center', marginTop: '24px' }}>
              {SUGGESTED.map((q, i) => (
                <button key={i} className="suggested-q" onClick={() => handleSend(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <div className="message-bubble">{renderFormattedContent(msg.content)}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-section">
                  <div className="evidence-label" style={{ marginTop: '8px' }}>
                    Evidence ({msg.sources.length} sources)
                  </div>
                  {msg.sources.map((src, si) => (
                    <EvidenceCard
                      key={si}
                      source={src}
                      onClick={() => setDrawerChunkId(src.chunk_id)}
                    />
                  ))}
                </div>
              )}
              {msg.confidence === 'insufficient' && msg.role === 'assistant' && (
                <div style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--text-tertiary)',
                  marginTop: '4px',
                }}>
                  Insufficient evidence in transcripts
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant">
              <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px', margin: 0 }} />
                Searching transcripts...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-wrapper">
          <input
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the expert interviews..."
            disabled={loading}
          />
          <button className="chat-send-btn" onClick={() => handleSend()} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>

      <EvidenceDrawer chunkId={drawerChunkId} onClose={() => setDrawerChunkId(null)} />
    </div>
  );
}
