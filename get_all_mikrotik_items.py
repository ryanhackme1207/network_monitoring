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

# 1. Get host info
host_res = api_call("host.get", {
    "hostids": ["10683"],
    "selectInterfaces": "extend",
}, auth=auth_token)

print("=== MikroTik Host Info in Zabbix ===")
for h in host_res["result"]:
    print(f"ID: {h['hostid']} | Name: {h['name']} | IP: {h['interfaces'][0]['ip']} | SNMP Status: {'ONLINE (GREEN)' if h['interfaces'][0]['available'] == '1' else 'UNKNOWN'}")

# 2. Get items with values
items_res = api_call("item.get", {
    "hostids": ["10683"],
    "output": ["name", "key_", "lastvalue"],
    "monitored": True
}, auth=auth_token)

print(f"\nTotal Items Monitoring MikroTik: {len(items_res.get('result', []))}")
print("\nSample Monitored Metrics:")
for item in items_res.get("result", [])[:30]:
    val = item.get("lastvalue", "Waiting for next poll")
    if val != "":
        print(f" - {item['name']}: {val}")
