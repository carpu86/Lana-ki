import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const API_BASE = import.meta.env.VITE_API_BASE || '';

function App() {
  const [message, setMessage] = useState('Hallo Lana, Status?');
  const [reply, setReply] = useState('Bereit.');
  const [busy, setBusy] = useState(false);

  async function sendMessage() {
    setBusy(true);
    setReply('Lana denkt...');
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setReply(data.answer || JSON.stringify(data));
    } catch (err) {
      setReply(`Backend nicht erreichbar: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">LANA-KI LOCAL FIRST</p>
        <h1>Deine lokale KI-Webapp ist bereit.</h1>
        <p className="subline">FastAPI Backend, Vite Frontend, Cloudflare-ready und ohne Secrets im Code.</p>
      </section>

      <section className="card">
        <label htmlFor="message">Nachricht an Lana</label>
        <textarea id="message" value={message} onChange={(e) => setMessage(e.target.value)} />
        <button onClick={sendMessage} disabled={busy}>{busy ? 'Sende...' : 'Senden'}</button>
        <div className="reply">{reply}</div>
      </section>

      <section className="grid">
        <div><strong>Backend</strong><span>/api/health + /api/chat</span></div>
        <div><strong>Modus</strong><span>local-first rescue upgrade</span></div>
        <div><strong>Secrets</strong><span>nur .env / 1Password, nie Git</span></div>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
