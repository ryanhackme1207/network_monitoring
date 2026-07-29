import json
import urllib.request

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

# Fetch all items for MikroTik (hostid: 10683)
items = api_call("item.get", {
    "output": ["itemid", "name", "key_", "lastvalue"],
    "hostids": ["10683"],
    "monitored": True
}, auth=auth_token)["result"]

print("========================================================================")
print("              MIKROTIK INTERFACE FULL SNMP MAPPING                      ")
print("========================================================================")

for item in sorted(items, key=lambda x: x.get('name','')):
    name = item.get('name', '')
    key = item.get('key_', '')
    val = item.get('lastvalue', '')
    if 'operational status' in name.lower() or 'interface' in name.lower() and ('speed' in name.lower() or 'type' in name.lower()):
        print(f"Name: {name:<48} | Key: {key:<35} | Value: {val}")

print("========================================================================")
