import json
import urllib.request
import time

ZABBIX_URL = "http://localhost:8080/api_jsonrpc.php"

def api_call(method, params, auth=None):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "auth": auth,
        "id": 1
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(ZABBIX_URL, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

login_res = api_call("user.login", {"username": "Admin", "password": "zabbix"})
auth_token = login_res["result"]

hosts_res = api_call("host.get", {
    "output": ["hostid", "name", "status"],
    "selectInterfaces": ["ip", "type", "available"],
    "filter": {"host": ["MikroTik-Router", "MikroTik-Internet-WAN", "MikroTik-Bridge-50"]}
}, auth=auth_token)

print("==========================================================================")
print("                       ZABBIX MIKROTIK MONITORING STATUS                  ")
print("==========================================================================")
for h in hosts_res.get("result", []):
    name = h["name"]
    ip = h["interfaces"][0]["ip"]
    interface_type = "SNMPv2" if h["interfaces"][0]["type"] == "2" else "ICMP Ping"
    print(f"[OK] Host: {name:<42} | IP: {ip:<15} | Type: {interface_type}")

print("==========================================================================")
