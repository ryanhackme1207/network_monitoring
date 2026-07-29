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

# Fetch items for MikroTik host 10683
items = api_call("item.get", {
    "output": ["itemid", "name", "delay"],
    "hostids": ["10683"],
    "monitored": True
}, auth=auth_token)["result"]

updated_count = 0
for item in items:
    if "Operational status" in item.get("name", ""):
        api_call("item.update", {
            "itemid": item["itemid"],
            "delay": "1s"
        }, auth=auth_token)
        print(f"Accelerated Zabbix SNMP item '{item['name']}' polling interval to 1s!")
        updated_count += 1

print(f"Total {updated_count} SNMP items accelerated to 1s real-time refresh speed!")
