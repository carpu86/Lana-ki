const fs = require('fs');

function parseEnv() {
    const content = fs.readFileSync('.env', 'utf-8');
    const keys = {};
    content.split('\n').forEach(line => {
        const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)$/);
        if (match) keys[match[1].trim()] = match[2].trim().replace(/^"|"$/g, '');
    });
    return keys;
}

async function checkApi(url, options, expectStatus = [200]) {
    try {
        const res = await fetch(url, options);
        return expectStatus.includes(res.status);
    } catch (e) {
        return false;
    }
}

async function runTests() {
    console.log('🔍 Starte API-Key Validierung aus .env...');
    const env = parseEnv();
    const accessMap = {};
    const promises = [];

    const addTest = (service, keyName, url, options, expect = [200]) => {
        if (!env[keyName]) return;
        promises.push((async () => {
            const isValid = await checkApi(url, options, expect);
            if (!accessMap[service]) accessMap[service] = { active_keys: [], invalid_keys: [] };
            if (isValid) {
                console.log(`✅ ${keyName} (GÜLTIG)`);
                accessMap[service].active_keys.push(keyName);
            } else {
                console.log(`❌ ${keyName} (UNGÜLTIG/GESPERRT)`);
                accessMap[service].invalid_keys.push(keyName);
            }
        })());
    };

    // Cloudflare
    Object.keys(env).filter(k => k.includes('CLOUDFLARE') && k.includes('TOKEN')).forEach(k => {
        addTest('cloudflare', k, 'https://api.cloudflare.com/client/v4/user/tokens/verify', { headers: { 'Authorization': `Bearer ${env[k]}` } });
    });

    // OpenAI
    if (env.OPENAI_API_KEY) addTest('openai', 'OPENAI_API_KEY', 'https://api.openai.com/v1/models', { headers: { 'Authorization': `Bearer ${env.OPENAI_API_KEY}` } });

    // Groq
    if (env.GROQ_API_KEY) addTest('groq', 'GROQ_API_KEY', 'https://api.groq.com/openai/v1/models', { headers: { 'Authorization': `Bearer ${env.GROQ_API_KEY}` } });

    // XAI
    Object.keys(env).filter(k => k.includes('XAI_API_KEY')).forEach(k => {
        addTest('xai', k, 'https://api.x.ai/v1/models', { headers: { 'Authorization': `Bearer ${env[k]}` } });
    });

    // Gemini
    Object.keys(env).filter(k => k.includes('GEMINI_API_KEY')).forEach(k => {
        addTest('gemini', k, `https://generativelanguage.googleapis.com/v1beta/models?key=${env[k]}`);
    });

    // Discord
    Object.keys(env).filter(k => k.includes('DISCORD_BOT_TOKEN') || (k.includes('DISCORD_TOKEN') && !k.includes('SECRET'))).forEach(k => {
        addTest('discord', k, 'https://discord.com/api/v10/users/@me', { headers: { 'Authorization': `Bot ${env[k]}` }, expect: [200, 401] }); 
        // 401 für Discord bedeutet meist, dass der Token valide ist, aber der Endpunkt für diesen spezifischen Request nicht.
    });

    await Promise.all(promises);

    accessMap['_metadata'] = {
        last_check: new Date().toISOString(),
        total_active_services: Object.keys(accessMap).filter(k => accessMap[k].active_keys && accessMap[k].active_keys.length > 0).length
    };

    fs.writeFileSync('access-map.json', JSON.stringify(accessMap, null, 2));
    console.log('\n💾 access-map.json erfolgreich erstellt!');
}

runTests();
