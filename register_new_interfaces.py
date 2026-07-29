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

new_hosts = [
    {
        "host": "MikroTik-Ether5-PPPoE",
        "name": "MikroTik ether5 (PPPoE 10.40.40.1)",
        "ip": "10.40.40.1"
    },
    {
        "host": "MikroTik-Ether2-8021x",
        "name": "MikroTik ether2 (802.1x 192.168.10.1)",
        "ip": "192.168.10.1"
    }
]

for h in new_hosts:
    existing = api_call("host.get", {"filter": {"host": [h["host"]]}}, auth=auth_token)
    if not existing.get("result"):
        res = api_call("host.create", {
            "host": h["host"],
            "name": h["name"],
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": h["ip"],
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [{"groupid": "5"}],
            "templates": [{"templateid": "10564"}] # ICMP Ping
        }, auth=auth_token)
        print(f"Registered {h['name']}:", res.get("result"))
    else:
        print(f"{h['name']} already exists.")
