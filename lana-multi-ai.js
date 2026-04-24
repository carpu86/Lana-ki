const express = require('express');
const axios = require('axios');
const OpenAI = require('openai');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const Groq = require('groq-sdk');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

// AI Clients initialisieren
let openai, gemini, groq;

try {
    if (process.env.OPENAI_API_KEY) {
        openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
        console.log('✅ OpenAI Client initialisiert');
    }
    if (process.env.GEMINI_API_KEY) {
        gemini = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
        console.log('✅ Gemini Client initialisiert');
    }
    if (process.env.GROQ_API_KEY) {
        groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
        console.log('✅ Groq Client initialisiert');
    }
} catch (error) {
    console.log('⚠️ AI Client Initialisierung:', error.message);
}

// Multi-AI Query Function
async function queryAI(message, provider) {
    try {
        switch (provider) {
            case 'openai':
                if (!openai) throw new Error('OpenAI nicht konfiguriert');
                const openaiResponse = await openai.chat.completions.create({
                    model: 'gpt-3.5-turbo',
                    messages: [{ role: 'user', content: message }],
                    max_tokens: 500
                });
                return {
                    provider: 'OpenAI',
                    response: openaiResponse.choices[0].message.content,
                    tokens: openaiResponse.usage.total_tokens
                };

            case 'gemini':
                if (!gemini) throw new Error('Gemini nicht konfiguriert');
                const model = gemini.getGenerativeModel({ model: 'gemini-pro' });
                const geminiResponse = await model.generateContent(message);
                return {
                    provider: 'Gemini',
                    response: geminiResponse.response.text()
                };

            case 'groq':
                if (!groq) throw new Error('Groq nicht konfiguriert');
                const groqResponse = await groq.chat.completions.create({
                    messages: [{ role: 'user', content: message }],
                    model: 'mixtral-8x7b-32768',
                    max_tokens: 500
                });
                return {
                    provider: 'Groq',
                    response: groqResponse.choices[0].message.content,
                    tokens: groqResponse.usage.total_tokens
                };

            case 'xai':
                if (!process.env.XAI_API_KEY_1) throw new Error('XAI nicht konfiguriert');
                const xaiResponse = await axios.post('https://api.x.ai/v1/chat/completions', {
                    model: 'grok-beta',
                    messages: [{ role: 'user', content: message }],
                    max_tokens: 500
                }, {
                    headers: {
                        'Authorization': 'Bearer ' + process.env.XAI_API_KEY_1,
                        'Content-Type': 'application/json'
                    }
                });
                return {
                    provider: 'XAI',
                    response: xaiResponse.data.choices[0].message.content,
                    tokens: xaiResponse.data.usage.total_tokens
                };

            default:
                throw new Error('Unbekannter Provider');
        }
    } catch (error) {
        return {
            provider: provider.toUpperCase(),
            error: error.message
        };
    }
}

// Health Check
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        service: 'LANA KI Multi-AI',
        version: '2.0.0',
        apis: {
            openai: !!process.env.OPENAI_API_KEY,
            gemini: !!process.env.GEMINI_API_KEY,
            groq: !!process.env.GROQ_API_KEY,
            xai: !!process.env.XAI_API_KEY_1
        },
        memory: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + 'MB'
    });
});

// Single AI Query
app.post('/api/query', async (req, res) => {
    const { message, provider } = req.body;
    if (!message) {
        return res.status(400).json({ error: 'Message erforderlich' });
    }
    const result = await queryAI(message, provider);
    res.json(result);
});

// Multi-AI Query (alle parallel)
app.post('/api/multi-query', async (req, res) => {
    const { message } = req.body;
    if (!message) {
        return res.status(400).json({ error: 'Message erforderlich' });
    }

    const providers = ['openai', 'gemini', 'groq', 'xai'];
    const promises = providers.map(provider => queryAI(message, provider));
    const results = await Promise.all(promises);

    res.json({
        message: message,
        timestamp: new Date().toISOString(),
        results: results
    });
});

// Main Interface
app.get('/', (req, res) => {
    const openaiStatus = process.env.OPENAI_API_KEY ? '✅' : '❌';
    const geminiStatus = process.env.GEMINI_API_KEY ? '✅' : '❌';
    const groqStatus = process.env.GROQ_API_KEY ? '✅' : '❌';
    const xaiStatus = process.env.XAI_API_KEY_1 ? '✅' : '❌';

    res.send(
        <h1>🎯 LANA KI - Multi-AI Interface v2.0</h1>
        <h2>✅ System läuft erfolgreich!</h2>
        <p><strong>APIs verfügbar:</strong></p>
        <ul>
            <li>OpenAI: </li>
            <li>Gemini: </li>
            <li>Groq: </li>
            <li>XAI: </li>
        </ul>
        
        <div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">
            <h3>🤖 Single AI Test</h3>
            <textarea id="singleMessage" placeholder="Deine Nachricht..." style="width: 100%; height: 60px;"></textarea><br>
            <select id="provider" style="margin: 10px 0; padding: 5px;">
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="groq">Groq</option>
                <option value="xai">XAI</option>
            </select>
            <button onclick="testSingleAI()" style="margin: 10px; padding: 10px 20px;">Testen</button>
            <div id="singleResult" style="margin-top: 10px; padding: 10px; background: #f5f5f5;"></div>
        </div>

        <div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">
            <h3>🚀 Multi-AI Test (Alle parallel)</h3>
            <textarea id="multiMessage" placeholder="Deine Nachricht..." style="width: 100%; height: 60px;"></textarea><br>
            <button onclick="testMultiAI()" style="margin: 10px 0; padding: 10px 20px;">Alle AIs Testen</button>
            <div id="multiResult" style="margin-top: 10px; padding: 10px; background: #f5f5f5;"></div>
        </div>

        <p><a href="/health">🔧 Health Check</a></p>
        <p><strong>💰 Revenue System bereit!</strong></p>

        <script>
        async function testSingleAI() {
            const message = document.getElementById('singleMessage').value;
            const provider = document.getElementById('provider').value;
            if (!message) return;
            
            document.getElementById('singleResult').innerHTML = '🔄 Lade...';
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, provider: provider})
                });
                const data = await response.json();
                document.getElementById('singleResult').innerHTML = 
                    data.error ? '❌ ' + data.error : '✅ ' + data.provider + ': ' + data.response;
            } catch (e) {
                document.getElementById('singleResult').innerHTML = '❌ Fehler: ' + e.message;
            }
        }

        async function testMultiAI() {
            const message = document.getElementById('multiMessage').value;
            if (!message) return;
            
            document.getElementById('multiResult').innerHTML = '🔄 Lade alle AIs...';
            try {
                const response = await fetch('/api/multi-query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                
                let html = '<h4>Ergebnisse von allen AIs:</h4>';
                data.results.forEach(result => {
                    if (result.error) {
                        html += '<p><strong>' + result.provider + ':</strong> ❌ ' + result.error + '</p>';
                    } else {
                        html += '<p><strong>' + result.provider + ':</strong> ✅ ' + result.response + '</p>';
                    }
                    html += '<hr>';
                });
                
                document.getElementById('multiResult').innerHTML = html;
            } catch (e) {
                document.getElementById('multiResult').innerHTML = '❌ Fehler: ' + e.message;
            }
        }
        </script>
    );
});

app.listen(PORT, () => {
    console.log('🎯 LANA KI Multi-AI gestartet!');
    console.log('================================');
    console.log('🌐 Server: http://localhost:' + PORT);
    console.log('📊 Health: http://localhost:' + PORT + '/health');
    console.log('🤖 Single API: http://localhost:' + PORT + '/api/query');
    console.log('🚀 Multi API: http://localhost:' + PORT + '/api/multi-query');
    console.log('================================');
    console.log('💾 RAM: ' + Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + 'MB');
    console.log('🚀 Bereit für Multi-AI Requests!');
    console.log('');
    console.log('📋 API Status:');
    console.log('OpenAI:', process.env.OPENAI_API_KEY ? '✅' : '❌');
    console.log('Gemini:', process.env.GEMINI_API_KEY ? '✅' : '❌');
    console.log('Groq:', process.env.GROQ_API_KEY ? '✅' : '❌');
    console.log('XAI:', process.env.XAI_API_KEY_1 ? '✅' : '❌');
});


