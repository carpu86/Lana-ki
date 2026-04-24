require('dotenv').config({ path: 'C:\\Carpuncle Cloud\\LanaApp\\.env' });
const express = require('express');
const app = express();
app.use(express.raw({ type: '*/*', limit: '200mb' }));

const TARGET = 'http://127.0.0.1:1234';
const LISTEN_HOST = '127.0.0.1';
const LISTEN_PORT = 4000;
const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.error('FEHLER: API_KEY ist nicht in .env konfiguriert.');
  process.exit(1);
}

app.all('*', async (req, res) => {
  try {
    const provided = req.header('x-api-key') || req.query.api_key;
    if (!provided || provided !== API_KEY) {
      return res.status(401).send('Invalid or missing API key');
    }

    const url = TARGET + req.originalUrl;
    const headers = { ...req.headers };
    delete headers.host; // Host wird vom Fetch gesetzt

    // Node 18+: globalThis.fetch ist vorhanden; fallback nicht nötig bei modernen Node
    const fetchFn = globalThis.fetch;
    const opts = {
      method: req.method,
      headers,
      body: ['GET','HEAD'].includes(req.method) ? undefined : req.body
    };

    const upstream = await fetchFn(url, opts);
    res.status(upstream.status);
    upstream.headers.forEach((v, k) => { res.setHeader(k, v); });
    const buffer = Buffer.from(await upstream.arrayBuffer());
    res.send(buffer);
  } catch (err) {
    console.error('Proxy error:', err);
    res.status(502).send('Bad Gateway: ' + err.message);
  }
});

app.listen(LISTEN_PORT, LISTEN_HOST, () => {
  console.log(`API-Key Proxy läuft auf http://${LISTEN_HOST}:${LISTEN_PORT} -> leitet an ${TARGET}`);
});
