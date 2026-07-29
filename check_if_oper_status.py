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

items_res = api_call("item.get", {
    "output": ["itemid", "name", "key_", "lastvalue"],
    "monitored": True
}, auth=auth_token)

print("=== All Discovered Interface Operational Status Items ===")
for item in items_res.get("result", []):
    name = item["name"]
    val = item.get("lastvalue", "N/A")
    if "operational status" in name.lower():
        # 1 = UP, 2 = DOWN
        status_str = "1 (UP - Cable Connected)" if val == "1" else ("2 (DOWN - Unplugged/No Carrier)" if val == "2" else f"Unknown ({val})")
        print(f"Port Item: {name:<50} | Value: {status_str}")
