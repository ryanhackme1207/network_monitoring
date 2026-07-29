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

hosts = api_call("host.get", {
    "output": ["hostid", "host", "name"],
    "selectInterfaces": ["ip", "type", "available"]
}, auth=auth_token)["result"]

print("==========================================================================")
print("                   ZABBIX HOST SNMP AVAILABILITY AUDIT                   ")
print("==========================================================================")
for h in hosts:
    if "MikroTik" in h["name"]:
        iface = h["interfaces"][0]
        ip = iface["ip"]
        if_type = "SNMP (port 161)" if iface["type"] == "2" else "Agent (port 10050)"
        avail = "GREEN (SNMP Connected)" if iface["available"] == "1" else ("WAITING FOR INITIAL POLL" if iface["available"] == "0" else "FAILED")
        print(f"Host: {h['name']:<42} | IP: {ip:<15} | Interface: {if_type} | Status: {avail}")
print("==========================================================================")
