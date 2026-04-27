import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API_BASE = "";

function App() {
  const [health, setHealth] = useState(null);
  const [message, setMessage] = useState("Lana, Systemstatus prüfen.");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadHealth() {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      setHealth({ ok: false, error: String(err) });
    }
  }

  async function sendMessage() {
    setBusy(true);
    setReply("");
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, mode: "local-first" }),
      });
      const data = await res.json();
      setReply(data.reply || JSON.stringify(data, null, 2));
    } catch (err) {
      setReply(`Fehler: ${String(err)}`);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <main className="shell">
      <section className="hero">
        <div className="badge">LOCAL-FIRST AI · LANA-KI</div>
        <h1>Lana KI ist online</h1>
        <p>
          Backend, Webapp und Cloudflare Tunnel sind gekoppelt. Diese Oberfläche
          läuft über denselben Backend-Port wie die Public-Domain.
        </p>

        <div className="cards">
          <div className="card">
            <span>Status</span>
            <strong>{health?.ok ? "ONLINE" : "PRÜFEN"}</strong>
          </div>
          <div className="card">
            <span>Mode</span>
            <strong>{health?.mode || "local-first"}</strong>
          </div>
          <div className="card">
            <span>Brain</span>
            <strong>{health?.brain_loaded ? "LOADED" : "UNKNOWN"}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>Chat-Test</h2>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
        />
        <button onClick={sendMessage} disabled={busy}>
          {busy ? "Lana arbeitet..." : "An Lana senden"}
        </button>
        {reply && <pre>{reply}</pre>}
      </section>

      <section className="panel small">
        <h2>API Health</h2>
        <pre>{JSON.stringify(health, null, 2)}</pre>
        <button onClick={loadHealth}>Status neu laden</button>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);