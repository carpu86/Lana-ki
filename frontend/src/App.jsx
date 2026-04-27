import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

function App() {
  const [health, setHealth] = useState(null);
  const [message, setMessage] = useState("Lana, prüfe Systemstatus.");
  const [reply, setReply] = useState("");

  async function loadHealth() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      setHealth({ ok: false, error: String(err) });
    }
  }

  async function sendMessage() {
    setReply("Lana verarbeitet...");
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, mode: "local-first" })
      });
      const data = await res.json();
      setReply(data.reply || JSON.stringify(data, null, 2));
    } catch (err) {
      setReply("Fehler: " + String(err));
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <main className="wrap">
      <header className="top">
        <div className="logo">🤖 <span>Lana KI</span></div>
        <div className={health?.ok ? "pill ok" : "pill warn"}>
          {health?.ok ? "ONLINE" : "CHECK"}
        </div>
      </header>

      <section className="hero">
        <div className="eyebrow">Carpuncle Cloud · Local First · Private AI</div>
        <h1>Deine KI.<br />Dein Server.</h1>
        <p>
          Lana läuft lokal auf deiner Infrastruktur, liefert eine Webapp aus
          und hält Secrets außerhalb des Git-Repositories.
        </p>
      </section>

      <section className="grid">
        <div className="card">
          <span>Status</span>
          <strong>{health?.ok ? "Backend OK" : "Nicht verbunden"}</strong>
        </div>
        <div className="card">
          <span>Mode</span>
          <strong>{health?.mode || "local-first"}</strong>
        </div>
        <div className="card">
          <span>Brain</span>
          <strong>{health?.brain_loaded ? "Loaded" : "Pending"}</strong>
        </div>
      </section>

      <section className="chat">
        <h2>Chat-Test</h2>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
        <button onClick={sendMessage}>An Lana senden</button>
        {reply && <pre>{reply}</pre>}
      </section>

      <section className="status">
        <h2>API Health</h2>
        <button onClick={loadHealth}>Neu prüfen</button>
        <pre>{JSON.stringify(health, null, 2)}</pre>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);