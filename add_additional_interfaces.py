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

hosts_to_add = [
    {
        "host": "MikroTik-Internet-WAN",
        "name": "MikroTik Internet WAN (192.168.31.219)",
        "ip": "192.168.31.219",
        "template": "10564" # ICMP Ping
    },
    {
        "host": "MikroTik-Bridge-50",
        "name": "MikroTik Bridge (192.168.50.1)",
        "ip": "192.168.50.1",
        "template": "10564" # ICMP Ping
    }
]

for item in hosts_to_add:
    existing = api_call("host.get", {"filter": {"host": [item["host"]]}}, auth=auth_token)
    if not existing.get("result"):
        res = api_call("host.create", {
            "host": item["host"],
            "name": item["name"],
            "interfaces": [
                {
                    "type": 1, # Agent/Ping
                    "main": 1,
                    "useip": 1,
                    "ip": item["ip"],
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [{"groupid": "5"}],
            "templates": [{"templateid": item["template"]}]
        }, auth=auth_token)
        print(f"Added {item['name']}:", res)
    else:
        print(f"{item['name']} already exists.")
