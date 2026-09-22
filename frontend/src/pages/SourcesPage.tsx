import React, { useState, useEffect } from 'react';
import type { DocumentSchema, DocumentDetailSchema } from '../types';
import { getTranscripts, getTranscript, uploadTranscriptFile, createTranscriptText } from '../services/api';

export default function SourcesPage() {
  const [docs, setDocs] = useState<DocumentSchema[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetailSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewerLoading, setViewerLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [countryFilter, setCountryFilter] = useState('');

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadTab, setUploadTab] = useState<'file' | 'text'>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [expertName, setExpertName] = useState('');
  const [expertRole, setExpertRole] = useState('');
  const [country, setCountry] = useState('');
  const [transcriptText, setTranscriptText] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSources();
  }, []);

  function loadSources() {
    setLoading(true);
    getTranscripts()
      .then(setDocs)
      .finally(() => setLoading(false));
  }

  async function openTranscript(id: string) {
    setViewerLoading(true);
    try {
      const detail = await getTranscript(id);
      setSelectedDoc(detail);
    } catch {}
    setViewerLoading(false);
  }

  async function handleFileUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadMsg(null);
    try {
      const res = await uploadTranscriptFile(selectedFile);
      setUploadMsg({ type: 'success', text: `Successfully ingested "${res.expert_name}" (${res.country}) — ${res.chunks_created} chunks created!` });
      setSelectedFile(null);
      loadSources();
      setTimeout(() => setShowUploadModal(false), 2000);
    } catch (err: any) {
      setUploadMsg({ type: 'error', text: err.message || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  }

  async function handleTextSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!expertName.trim() || !country.trim() || !transcriptText.trim()) {
      setUploadMsg({ type: 'error', text: 'Expert Name, Country, and Transcript Text are required.' });
      return;
    }

    setUploading(true);
    setUploadMsg(null);
    try {
      const res = await createTranscriptText({
        expert_name: expertName.trim(),
        expert_role: expertRole.trim() || 'Expert',
        country: country.trim(),
        raw_text: transcriptText.trim(),
      });
      setUploadMsg({ type: 'success', text: `Successfully ingested "${res.expert_name}" (${res.country}) — ${res.chunks_created} chunks created!` });
      setExpertName('');
      setExpertRole('');
      setCountry('');
      setTranscriptText('');
      loadSources();
      setTimeout(() => setShowUploadModal(false), 2000);
    } catch (err: any) {
      setUploadMsg({ type: 'error', text: err.message || 'Creation failed' });
    } finally {
      setUploading(false);
    }
  }

  const getCountryClass = (country: string) => {
    if (country.toLowerCase().includes('france')) return 'france';
    if (country.toLowerCase().includes('germany')) return 'germany';
    if (country.toLowerCase().includes('uk') || country.toLowerCase().includes('united kingdom')) return 'uk';
    return '';
  };

  const filteredDocs = docs.filter((d) => {
    if (countryFilter && d.country !== countryFilter) return false;
    if (search) {
      const s = search.toLowerCase();
      return d.expert_name.toLowerCase().includes(s) || d.country.toLowerCase().includes(s);
    }
    return true;
  });

  const filteredChunks = selectedDoc?.chunks.filter((c) => {
    if (!search) return true;
    return c.text.toLowerCase().includes(search.toLowerCase()) ||
           c.speaker.toLowerCase().includes(search.toLowerCase());
  });

  if (loading && docs.length === 0) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner" />
          <span>Loading sources...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Sources</h2>
          <p className="subtitle">Transcript library — the source of truth for all analysis.</p>
        </div>
        <button
          className="btn btn-primary"
          style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '6px' }}
          onClick={() => {
            setUploadMsg(null);
            setShowUploadModal(true);
          }}
        >
          <span>＋</span> Add Transcript
        </button>
      </div>

      {/* Filters */}
      <div className="filter-bar">
        <button
          className={`filter-chip ${countryFilter === '' ? 'active' : ''}`}
          onClick={() => setCountryFilter('')}
        >
          All Markets
        </button>
        {Array.from(new Set(docs.map((d) => d.country))).map((c) => (
          <button
            key={c}
            className={`filter-chip ${countryFilter === c ? 'active' : ''}`}
            onClick={() => setCountryFilter(countryFilter === c ? '' : c)}
          >
            {c}
          </button>
        ))}
      </div>

      {!selectedDoc ? (
        /* Source Cards */
        <div className="market-cards">
          {filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className={`source-card ${getCountryClass(doc.country)}`}
              onClick={() => openTranscript(doc.id)}
            >
              <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '4px' }}>
                {doc.country}
              </h3>
              <p style={{ fontWeight: 600, marginBottom: '2px' }}>{doc.expert_name}</p>
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                {doc.expert_role}
              </p>
              <div className="market-detail-item">
                <span className="detail-label">Segments</span>
                <span className="detail-value">{doc.chunk_count}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Transcript Viewer */
        <div>
          <button
            className="btn btn-outline"
            style={{ marginBottom: '16px' }}
            onClick={() => setSelectedDoc(null)}
          >
            ← Back to sources
          </button>

          <div className="transcript-viewer">
            <div className="transcript-viewer-header">
              <div>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>
                  {selectedDoc.expert_name}
                </h3>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                  {selectedDoc.expert_role} · {selectedDoc.country}
                </p>
              </div>
              <input
                className="transcript-search"
                placeholder="Search transcript..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {viewerLoading ? (
              <div className="loading-container"><div className="spinner" /></div>
            ) : (
              filteredChunks?.map((chunk) => (
                <div
                  key={chunk.id}
                  className={`transcript-turn ${search && chunk.text.toLowerCase().includes(search.toLowerCase()) ? 'highlight' : ''}`}
                >
                  <span className="turn-timestamp">{chunk.timestamp}</span>
                  <div className="turn-content">
                    <div className="turn-speaker">{chunk.speaker}</div>
                    <div className="turn-text">{chunk.text}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Add Transcript Modal */}
      {showUploadModal && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="modal-content" style={{
            background: 'var(--bg-surface, #1e222d)',
            color: 'var(--text-primary, #ffffff)',
            borderRadius: '12px',
            padding: '24px',
            maxWidth: '560px',
            width: '90%',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            border: '1px solid var(--border-color, #2f3542)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Add New Transcript</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                style={{ background: 'none', border: 'none', color: '#999', fontSize: '1.5rem', cursor: 'pointer' }}
              >
                ×
              </button>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', borderBottom: '1px solid #333', paddingBottom: '8px' }}>
              <button
                className={`filter-chip ${uploadTab === 'file' ? 'active' : ''}`}
                onClick={() => setUploadTab('file')}
                type="button"
              >
                📁 Upload Document (.pdf, .docx, .txt)
              </button>
              <button
                className={`filter-chip ${uploadTab === 'text' ? 'active' : ''}`}
                onClick={() => setUploadTab('text')}
                type="button"
              >
                ✍ Paste Text
              </button>
            </div>

            {uploadMsg && (
              <div style={{
                padding: '10px 14px',
                borderRadius: '6px',
                marginBottom: '16px',
                fontSize: '0.9rem',
                backgroundColor: uploadMsg.type === 'success' ? 'rgba(46, 204, 113, 0.2)' : 'rgba(231, 76, 60, 0.2)',
                color: uploadMsg.type === 'success' ? '#2ecc71' : '#e74c3c',
                border: `1px solid ${uploadMsg.type === 'success' ? '#2ecc71' : '#e74c3c'}`,
              }}>
                {uploadMsg.text}
              </div>
            )}

            {uploadTab === 'file' ? (
              <form onSubmit={handleFileUpload}>
                <p style={{ fontSize: '0.85rem', color: '#aaa', marginBottom: '12px' }}>
                  Upload a <code>.pdf</code>, <code>.docx</code>, <code>.doc</code>, or <code>.txt</code> file formatted with an Expert header and timestamped turns (e.g. <code>00:15 Interviewer: ...</code>).
                </p>
                <div style={{
                  border: '2px dashed #444',
                  borderRadius: '8px',
                  padding: '24px',
                  textAlign: 'center',
                  marginBottom: '16px',
                  cursor: 'pointer',
                }}>
                  <input
                    type="file"
                    accept=".txt,.pdf,.docx,.doc,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword,text/plain"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    style={{ width: '100%' }}
                  />
                  {selectedFile && (
                    <p style={{ marginTop: '8px', fontSize: '0.85rem', color: '#2ecc71' }}>
                      Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button type="button" className="btn btn-outline" onClick={() => setShowUploadModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={!selectedFile || uploading}>
                    {uploading ? 'Ingesting...' : 'Ingest Transcript'}
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleTextSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaa', marginBottom: '4px' }}>Expert Name *</label>
                    <input
                      style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: '#13161c', border: '1px solid #333', color: '#fff' }}
                      placeholder="e.g. Dr. Maria Garcia"
                      value={expertName}
                      onChange={(e) => setExpertName(e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaa', marginBottom: '4px' }}>Country / Market *</label>
                    <input
                      style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: '#13161c', border: '1px solid #333', color: '#fff' }}
                      placeholder="e.g. Spain"
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '12px' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaa', marginBottom: '4px' }}>Role / Specialty</label>
                  <input
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: '#13161c', border: '1px solid #333', color: '#fff' }}
                    placeholder="e.g. Chief of Robotic Surgery"
                    value={expertRole}
                    onChange={(e) => setExpertRole(e.target.value)}
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#aaa', marginBottom: '4px' }}>Timestamped Transcript Body *</label>
                  <textarea
                    rows={8}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: '6px', background: '#13161c', border: '1px solid #333', color: '#fff', fontSize: '0.85rem', fontFamily: 'monospace' }}
                    placeholder={`00:00\nInterviewer: How is adoption in your market?\n\n00:18\nDr. Garcia: Adoption is accelerating in large regional centers...`}
                    value={transcriptText}
                    onChange={(e) => setTranscriptText(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button type="button" className="btn btn-outline" onClick={() => setShowUploadModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={uploading}>
                    {uploading ? 'Ingesting...' : 'Ingest & Index'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

