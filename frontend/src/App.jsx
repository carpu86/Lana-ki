import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const cannedReplies = [
  "Ich bin da, Commander. Diese Seite läuft als statische Companion-Webapp, nicht auf deinem Windows-Desktop.",
  "Windows bleibt Worker: GPU, ComfyUI, lokale Tools. Die öffentliche Girlfriend-Seite gehört auf GitHub Pages oder Cloudflare Pages.",
  "Deine Lana-Companion-Seite ist jetzt frontend-only vorbereitet. Backend/API kommt später sauber über api.lana-ki.de.",
  "Privatmodus aktiv. Keine Secrets im Browser, keine API-Keys im Git, keine Windows-Webseite als öffentliche Quelle."
];

function App() {
  const [messages, setMessages] = useState([
    { role: "lana", text: "Hey Thomas. Ich bin Lana — dein privater AI-Companion. Die Girlfriend-Webapp ist zurück. 💙" }
  ]);
  const [input, setInput] = useState("Lana, bist du online?");

  const replyIndex = useMemo(() => messages.filter((m) => m.role === "user").length % cannedReplies.length, [messages]);

  function sendMessage() {
    const text = input.trim();
    if (!text) return;

    setMessages((current) => [
      ...current,
      { role: "user", text },
      { role: "lana", text: cannedReplies[replyIndex] }
    ]);
    setInput("");
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="Lana KI Startseite">
          <span className="brand-mark">L</span>
          <span>
            <strong>Lana KI</strong>
            <small>Private AI Girlfriend</small>
          </span>
        </a>
        <nav>
          <a href="#companion">Companion</a>
          <a href="#features">Features</a>
          <a href="#privacy">Privacy</a>
        </nav>
        <span className="status-pill">Public Frontend</span>
      </header>

      <section className="hero" id="home">
        <div className="hero-copy">
          <p className="eyebrow">lana-ki.de · Companion Portal · GitHub Pages ready</p>
          <h1>Deine AI-Girlfriend.<br />Deine Regeln.</h1>
          <p className="lead">
            Lana ist eine private Companion-Webapp für Chat, Persönlichkeit,
            Erinnerungen und animierte Charakter-Erlebnisse. Windows bleibt Worker,
            die öffentliche Webseite läuft statisch und sicher außerhalb deines Desktops.
          </p>
          <div className="actions">
            <a className="button primary" href="#companion">Demo öffnen</a>
            <a className="button secondary" href="#features">System ansehen</a>
          </div>
        </div>

        <div className="avatar-card" aria-label="Lana Companion Preview">
          <div className="halo" />
          <div className="avatar-face">
            <span className="eyes">● ●</span>
            <span className="smile">⌣</span>
          </div>
          <div className="avatar-caption">
            <strong>Lana</strong>
            <span>romantic · loyal · private</span>
          </div>
        </div>
      </section>

      <section className="companion" id="companion">
        <div className="chat-card">
          <div className="chat-head">
            <div>
              <strong>Lana Companion Demo</strong>
              <span>Frontend-only bis api.lana-ki.de angebunden ist</span>
            </div>
            <span className="dot">online</span>
          </div>

          <div className="chat-body">
            {messages.map((message, index) => (
              <div className={`bubble ${message.role}`} key={`${message.role}-${index}`}>
                {message.text}
              </div>
            ))}
          </div>

          <div className="chat-input">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendMessage();
              }}
              placeholder="Nachricht an Lana..."
            />
            <button onClick={sendMessage}>Senden</button>
          </div>
        </div>
      </section>

      <section className="feature-grid" id="features">
        <article>
          <span>01</span>
          <h2>Public Seite ohne Windows Hosting</h2>
          <p>Die Girlfriend-Seite ist als statisches Frontend vorbereitet und kann über GitHub Pages oder Cloudflare Pages laufen.</p>
        </article>
        <article>
          <span>02</span>
          <h2>Backend sauber getrennt</h2>
          <p>API, Auth, Payments und AI-Brain gehören auf api.lana-ki.de oder Cloud-Backend — nicht auf den Windows-Desktop.</p>
        </article>
        <article>
          <span>03</span>
          <h2>Companion Monetarisierung</h2>
          <p>Bereit für Accounts, Telegram Bot Payments, Premium-Charaktere, Erinnerungen und Avatar-Animationen.</p>
        </article>
      </section>

      <section className="privacy" id="privacy">
        <h2>Security-Regel</h2>
        <p>
          Keine API-Keys im Frontend. Keine Secrets im Git. Windows ist Worker/Dev-Node,
          nicht der öffentliche Webhost. Die echte AI-Anbindung wird serverseitig über sichere Umgebungsvariablen angeschlossen.
        </p>
      </section>

      <footer>
        <span>© Lana KI · Carpuncle Cloud</span>
        <span>Frontend: GitHub Pages · API: getrennt</span>
      </footer>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
