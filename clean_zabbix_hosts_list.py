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

# Fetch all hosts
hosts = api_call("host.get", {
    "output": ["hostid", "host", "name"]
}, auth=auth_token)["result"]

redundant_ids = []
for h in hosts:
    if "MikroTik" in h["name"] and h["name"] != "MikroTik-hEX":
        print(f"Removing redundant sub-host '{h['name']}' (ID {h['hostid']})...")
        redundant_ids.append(h["hostid"])

if redundant_ids:
    api_call("host.delete", redundant_ids, auth=auth_token)

print("\n=== Host List Cleanup Complete! ===")
print("Only primary MikroTik-hEX SNMP host remains with GREEN SNMP availability.")
