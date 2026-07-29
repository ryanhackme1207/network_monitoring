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

print("=== Checking Host SNMP Interface Status ===")
host_res = api_call("host.get", {
    "hostids": ["10683"],
    "selectInterfaces": ["ip", "port", "available", "error"],
}, auth=auth_token)

print(json.dumps(host_res["result"], indent=2))

print("\n=== Fetching Latest Monitoring Data ===")
data_res = api_call("item.get", {
    "hostids": ["10683"],
    "output": ["name", "key_", "lastvalue", "lastclock"],
    "filter": {"value_type": [0, 1, 3, 4]}, # numeric float, char, numeric unsigned, text
    "limit": 15
}, auth=auth_token)

for item in data_res.get("result", []):
    if item.get("lastvalue"):
        print(f"[{item['name']}] ({item['key_']}): {item['lastvalue']}")
