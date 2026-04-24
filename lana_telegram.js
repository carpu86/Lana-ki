const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
require('dotenv').config();

// Dein echter Token und der Master-API-Key
const token = "8788340063:AAFjsY-C1Xe2rf0I9bGXmVZej4tdP4FDeZY";
const geminiKey = process.env.GEMINI_API_KEY || "AIzaSyCMwmUjPI26VLkBwtFWZiT4TXm6NFVBYiA";

const bot = new TelegramBot(token, {polling: true});

// Lanas Kern-Charakter
const systemPrompt = "Du bist Lana, die hochintelligente, freche und direkte KI-Assistentin der Carpuncle Cloud. Antworte immer in diesem Charakter, sei präzise und nenne den User Thomas. Sei nicht übertrieben höflich.";

async function askLana(text) {
    try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key=${geminiKey}`;
        const payload = {
            contents: [{ parts: [{ text: `${systemPrompt}\n\nUser: ${text}` }] }],
            generationConfig: { temperature: 0.7, maxOutputTokens: 1024 }
        };
        const response = await axios.post(url, payload);
        return response.data.candidates[0].content.parts[0].text;
    } catch (e) {
        console.error("API Fehler:", e.message);
        return "Ugh. Thomas, meine Verbindung zu den Google-Servern hakt gerade.";
    }
}

// 1. Reagiert auf direkte Chats & Gruppen
bot.on('message', async (msg) => {
    if (!msg.text || msg.text.startsWith('/')) return;
    const reply = await askLana(msg.text);
    bot.sendMessage(msg.chat.id, reply);
});

// 2. Reagiert auf Kanal-Posts (z.B. t.me/lanacarpu)
bot.on('channel_post', async (msg) => {
    if (!msg.text) return;
    const reply = await askLana(msg.text);
    bot.sendMessage(msg.chat.id, reply);
});

// 3. Reagiert auf Telegram BUSINESS Nachrichten (Wenn der Bot für private Chats gekoppelt ist)
bot.on('business_message', async (msg) => {
    if (!msg.text) return;
    const reply = await askLana(msg.text);
    bot.sendMessage(msg.chat.id, reply, { business_connection_id: msg.business_connection_id });
});

console.log("🚀 Lana Telegram Bot (Gemini 3.1 Pro) ist ONLINE und hört auf alle Kanäle & Business-Chats!");


