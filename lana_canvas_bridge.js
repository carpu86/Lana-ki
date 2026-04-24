const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());
const PORT = 8090; // Eigener Port für Microsoft Canvas

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || "AIzaSyCMwmUjPI26VLkBwtFWZiT4TXm6NFVBYiA";
const CANVAS_APP_ID = "7f881695-a2e5-4f57-8e04-ca8261d3dc5b"; // Deine spezifische App-ID

const systemPrompt = "Du bist Lana, die KI-Assistentin der Carpuncle Cloud. Du antwortest auf Anfragen aus dem Microsoft Lana Ops Canvas. Sei präzise, freundlich und extrem professionell.";

app.post('/api/canvas', async (req, res) => {
    try {
        const { message, appId, sessionId } = req.body;
        
        // Sicherheits-Check: Ist das wirklich DEINE Canvas App?
        if (appId !== CANVAS_APP_ID) {
            console.log("❌ Unautorisierter Canvas-Zugriff blockiert!");
            return res.status(403).json({ error: "Unauthorized App ID" });
        }

        console.log(`📥 Anfrage von Lana Ops Canvas erhalten (Session: ${sessionId})`);

        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`;
        const payload = {
            contents: [{ parts: [{ text: `${systemPrompt}\n\nCanvas User: ${message}` }] }],
            generationConfig: { temperature: 0.7, maxOutputTokens: 2048 }
        };

        const response = await axios.post(url, payload);
        const reply = response.data.candidates[0].content.parts[0].text;
        
        // Antwort zurück an Microsoft senden
        res.json({ reply: reply, status: "success" });

    } catch (error) {
        console.error("API Fehler:", error.message);
        res.status(500).json({ error: "Lanas Kern ist gerade offline." });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Microsoft Canvas Bridge läuft auf Port ${PORT} für App-ID: ${CANVAS_APP_ID}`);
});
