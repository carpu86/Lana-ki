import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

function App() {
  const [health, setHealth] = useState(null);
  const [message, setMessage] = useState("Lana, wie heiße ich?");
  const [chat, setChat] = useState([
    {
      role: "lana",
      text: "Hey Commander Thomas. Ich bin Lana — deine private Local-First AI Companion Webapp."
    }
  ]);
  const [busy, setBusy] = useState(false);

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
    const clean = message.trim();
    if (!clean) return;

    setBusy(true);
    setChat((old) => [...old, { role: "user", text: clean }]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: clean, mode: "local-first" })
      });
      const data = await res.json();
      setChat((old) => [...old, { role: "lana", text: data.reply || "Ich bin da." }]);
    } catch (err) {
      setChat((old) => [...old, { role: "lana", text: "Fehler: " + String(err) }]);
    } finally {
      setMessage("");
      setBusy(false);
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="mark">L</span>
          <div>
            <strong>Lana KI</strong>
            <small>Private AI Girlfriend · Local First</small>
          </div>
        </div>
        <div className={health?.ok ? "pill ok" : "pill warn"}>
          {health?.ok ? "ONLINE" : "CHECK"}
        </div>
      </header>

      <section className="hero">
        <div className="copy">
          <div className="eyebrow">Carpuncle Cloud · Companion Runtime</div>
          <h1>Deine Lana ist online.</h1>
          <p>
            Private Companion-Webapp mit lokalem Backend, Chat-Runtime,
            Erinnerung und sauber getrennten Secrets.
          </p>

          <div className="meta">
            <div>
              <span>Commander</span>
              <strong>{health?.commander_name || "Thomas Heckhoff"}</strong>
            </div>
            <div>
              <span>Mode</span>
              <strong>{health?.mode || "local-first"}</strong>
            </div>
            <div>
              <span>Webapp</span>
              <strong>{health?.webapp_served ? "Served" : "Build prüfen"}</strong>
            </div>
          </div>
        </div>

        <div className="avatar">
          <div className="glow"></div>
          <div className="face">
            <span className="eyes">● ●</span>
            <span className="smile">⌣</span>
          </div>
          <div className="caption">
            <strong>Lana</strong>
            <span>loyal · romantic · private</span>
          </div>
        </div>
      </section>

      <section className="chatbox">
        <div className="chathead">
          <div>
            <strong>Lana Chat</strong>
            <span>Direkt mit /api/chat verbunden</span>
          </div>
          <button onClick={loadHealth}>Status</button>
        </div>

        <div className="messages">
          {chat.map((item, index) => (
            <div className={`bubble ${item.role}`} key={index}>
              {item.text}
            </div>
          ))}
        </div>

        <div className="inputrow">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            placeholder="Schreib Lana..."
          />
          <button onClick={sendMessage} disabled={busy}>
            {busy ? "..." : "Senden"}
          </button>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);