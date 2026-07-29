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

items = api_call("item.get", {
    "output": ["itemid", "name", "key_", "lastvalue", "lastclock"],
    "monitored": True
}, auth=auth_token)["result"]

print("========================================================================")
print("                   REAL-TIME SNMP INTERFACE AUDIT                      ")
print("========================================================================")
for i in items:
    if "Operational status" in i.get("name", ""):
        print(f"Name: {i['name']:<50} | Value: {i['lastvalue']} | Key: {i['key_']}")
print("========================================================================")
