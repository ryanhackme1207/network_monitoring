const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const ZABBIX_URL = process.env.ZABBIX_URL || 'http://localhost:8080/api_jsonrpc.php';
const ZABBIX_USER = process.env.ZABBIX_USER || 'Admin';
const ZABBIX_PASS = process.env.ZABBIX_PASS || 'zabbix';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Enable CORS and anti-caching headers for ultra-fast Netlify cross-domain access (ryan-sec.dev)
app.use((req, res, next) => {
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    }
    next();
});

let zabbixToken = null;

async function getZabbixToken() {
    try {
        const resp = await fetch(ZABBIX_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'user.login',
                params: { username: ZABBIX_USER, password: ZABBIX_PASS },
                id: 1
            })
        });
        const data = await resp.json();
        if (data.result) {
            zabbixToken = data.result;
            return zabbixToken;
        }
    } catch (e) {
        console.error('Failed to authenticate with Zabbix API:', e.message);
    }
    return null;
}

// Ultra-lightweight endpoint: returns ONLY the MikroTik port statuses (1KB payload, <15ms response)
app.get('/api/network-status', async (req, res) => {
    if (!zabbixToken) {
        await getZabbixToken();
    }

    try {
        // Fetch only MikroTik (hostid: 10683) operational status & uptime items
        const itemsResp = await fetch(ZABBIX_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'item.get',
                params: {
                    output: ['itemid', 'hostid', 'name', 'key_', 'lastvalue', 'lastclock'],
                    hostids: ['10683'],
                    monitored: true
                },
                auth: zabbixToken,
                id: 2
            })
        });
        const itemsData = await itemsResp.json();

        if (itemsData.error) {
            await getZabbixToken();
        }

        // Fetch active problems for MikroTik
        const probResp = await fetch(ZABBIX_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'problem.get',
                params: {
                    output: ['eventid', 'objectid', 'name', 'severity', 'clock'],
                    hostids: ['10683'],
                    recent: true
                },
                auth: zabbixToken,
                id: 3
            })
        });
        const probData = await probResp.json();

        res.json({
            success: true,
            items: itemsData.result || [],
            problems: probData.result || [],
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`MikroTik Network Dashboard Server running at http://localhost:${PORT}`);
});
