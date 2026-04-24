require('dotenv').config();
const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
app.use(express.json());

// API Provider Integration (liest sicher aus .env)
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

app.post('/api/chat', async (req, res) => {
    try {
        const message = req.body.message;
        // Gemini Core
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
        const result = await model.generateContent(message);
        const response = await result.response;

        res.json({
            unified_response: response.text(),
            provider: "Gemini (Lana Multi-AI Gateway)",
            status: "success"
        });
    } catch (error) {
        console.error("Gateway Error:", error);
        res.status(500).json({ error: error.message, status: "failed" });
    }
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
    console.log(`🤖 Lana Multi-AI Gateway online auf Port ${PORT}`);
});
