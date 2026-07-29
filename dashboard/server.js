const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const ZABBIX_URL = process.env.ZABBIX_URL || 'http://localhost:8080/api_jsonrpc.php';
const ZABBIX_USER = process.env.ZABBIX_USER || 'Admin';
const ZABBIX_PASS = process.env.ZABBIX_PASS || 'zabbix';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

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

// Endpoint to fetch network status
app.get('/api/network-status', async (req, res) => {
    if (!zabbixToken) {
        await getZabbixToken();
    }

    try {
        // Fetch all items from Zabbix (including physical ifOperStatus)
        const itemsResp = await fetch(ZABBIX_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'item.get',
                params: {
                    output: ['itemid', 'hostid', 'name', 'key_', 'lastvalue', 'lastclock'],
                    monitored: true
                },
                auth: zabbixToken,
                id: 2
            })
        });
        const itemsData = await itemsResp.json();

        // Fetch active problems
        const probResp = await fetch(ZABBIX_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'problem.get',
                params: {
                    output: ['eventid', 'objectid', 'name', 'severity', 'clock'],
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
