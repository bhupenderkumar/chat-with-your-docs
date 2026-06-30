'use client';

import { useState } from 'react';

export default function HomePage() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setStatus('Please select at least one file.');
      return;
    }

    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append('files', file));

    setStatus('Uploading and indexing documents...');
    const response = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setStatus(data.message || 'Upload complete.');
  };

  const handleChat = async () => {
    if (!question.trim()) {
      setStatus('Please enter a question.');
      return;
    }

    setLoading(true);
    setStatus('Asking the assistant...');
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    setAnswer(data.answer || 'No answer available.');
    setStatus('Done.');
    setLoading(false);
  };

  return (
    <main style={{ maxWidth: 900, margin: '40px auto', padding: 24 }}>
      <h1 style={{ fontSize: 32, marginBottom: 8 }}>Chat With Your Docs</h1>
      <p style={{ color: '#4b5563', marginBottom: 24 }}>
        Upload documents and ask questions about them. If the answer is not in the uploaded content, the assistant will say so.
      </p>

      <div style={{ background: '#fff', padding: 20, borderRadius: 12, boxShadow: '0 2px 10px rgba(0,0,0,0.06)', marginBottom: 20 }}>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Upload documents</h2>
        <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
        <button onClick={handleUpload} style={{ marginLeft: 12, padding: '8px 14px', borderRadius: 8, border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>
          Upload
        </button>
        <p style={{ color: '#374151', marginTop: 10 }}>{status}</p>
      </div>

      <div style={{ background: '#fff', padding: 20, borderRadius: 12, boxShadow: '0 2px 10px rgba(0,0,0,0.06)' }}>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Ask a question</h2>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask anything about your uploaded documents"
          style={{ width: '100%', minHeight: 100, padding: 10, borderRadius: 8, border: '1px solid #d1d5db' }}
        />
        <button onClick={handleChat} disabled={loading} style={{ marginTop: 10, padding: '10px 16px', borderRadius: 8, border: 'none', background: '#111827', color: 'white', cursor: 'pointer' }}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
        <div style={{ marginTop: 20, whiteSpace: 'pre-wrap', color: '#111827' }}>{answer}</div>
      </div>
    </main>
  );
}
