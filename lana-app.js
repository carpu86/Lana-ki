const express = require('express');
const axios = require('axios');
const OpenAI = require('openai');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

// OpenAI Client
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// Health Check
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        service: 'LANA KI',
        version: '1.0.0',
        apis: {
            openai: !!process.env.OPENAI_API_KEY,
            gemini: !!process.env.GEMINI_API_KEY,
            groq: !!process.env.GROQ_API_KEY,
            xai: !!process.env.XAI_API_KEY
        },
        memory: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + 'MB'
    });
});

// AI Query Endpoint
app.post('/api/query', async (req, res) => {
    const { message, provider } = req.body;
    
    if (!message) {
        return res.status(400).json({ error: 'Message erforderlich' });
    }
    
    try {
        let result;
        
        if (provider === 'openai' && process.env.OPENAI_API_KEY) {
            const response = await openai.chat.completions.create({
                model: 'gpt-3.5-turbo',
                messages: [{ role: 'user', content: message }],
                max_tokens: 500
            });
            result = {
                provider: 'OpenAI',
                response: response.choices[0].message.content,
                tokens: response.usage.total_tokens
            };
        } else {
            result = { error: 'Provider nicht verfügbar oder nicht konfiguriert' };
        }
        
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Main Interface
app.get('/', (req, res) => {
    const openaiStatus = process.env.OPENAI_API_KEY ? '✅' : '❌';
    const geminiStatus = process.env.GEMINI_API_KEY ? '✅' : '❌';
    const groqStatus = process.env.GROQ_API_KEY ? '✅' : '❌';
    const xaiStatus = process.env.XAI_API_KEY ? '✅' : '❌';
    
    res.send('<h1>🎯 LANA KI - Multi-AI Interface</h1>' +
             '<h2>✅ System läuft erfolgreich!</h2>' +
             '<p><strong>APIs verfügbar:</strong></p>' +
             '<ul>' +
             '<li>OpenAI: ' + openaiStatus + '</li>' +
             '<li>Gemini: ' + geminiStatus + '</li>' +
             '<li>Groq: ' + groqStatus + '</li>' +
             '<li>XAI: ' + xaiStatus + '</li>' +
             '</ul>' +
             '<div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">' +
             '<h3>🤖 AI Test Interface</h3>' +
             '<textarea id="message" placeholder="Deine Nachricht..." style="width: 100%; height: 60px;"></textarea><br>' +
             '<button onclick="testAI()" style="margin: 10px 0; padding: 10px 20px;">OpenAI Testen</button>' +
             '<div id="result" style="margin-top: 10px; padding: 10px; background: #f5f5f5;"></div>' +
             '</div>' +
             '<p><a href="/health">🔧 Health Check</a></p>' +
             '<p><strong>💰 Revenue System bereit!</strong></p>' +
             '<script>' +
             'async function testAI() {' +
             '  const message = document.getElementById("message").value;' +
             '  if (!message) return;' +
             '  document.getElementById("result").innerHTML = "🔄 Lade...";' +
             '  try {' +
             '    const response = await fetch("/api/query", {' +
             '      method: "POST",' +
             '      headers: {"Content-Type": "application/json"},' +
             '      body: JSON.stringify({message: message, provider: "openai"})' +
             '    });' +
             '    const data = await response.json();' +
             '    document.getElementById("result").innerHTML = data.error ? "❌ " + data.error : "✅ " + data.response;' +
             '  } catch (e) {' +
             '    document.getElementById("result").innerHTML = "❌ Fehler: " + e.message;' +
             '  }' +
             '}' +
             '</script>');
});

app.listen(PORT, () => {
    console.log('🎯 LANA KI gestartet!');
    console.log('================================');
    console.log('🌐 Server: http://localhost:' + PORT);
    console.log('📊 Health: http://localhost:' + PORT + '/health');
    console.log('🤖 API: http://localhost:' + PORT + '/api/query');
    console.log('================================');
    console.log('💾 RAM: ' + Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + 'MB');
    console.log('🚀 Bereit für Multi-AI Requests!');
});
