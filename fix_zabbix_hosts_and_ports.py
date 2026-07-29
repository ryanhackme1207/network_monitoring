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

# 1. Fetch all hosts
hosts = api_call("host.get", {
    "output": ["hostid", "host", "name"],
    "selectInterfaces": "extend"
}, auth=auth_token)["result"]

print("=== Converting All MikroTik Host Interfaces to SNMP (port 161) ===")
for h in hosts:
    if "MikroTik" in h["name"]:
        host_id = h["hostid"]
        interfaces = h.get("interfaces", [])
        
        # Check if interface is agent (type 1) or snmp (type 2)
        needs_update = False
        for iface in interfaces:
            if iface["type"] == "1": # Change from Agent (10050) to SNMP (161)
                needs_update = True
                
        if needs_update:
            print(f"Updating host '{h['name']}' (ID {host_id}) interface to SNMP port 161...")
            # Remove old interface and replace with SNMP interface
            ip = interfaces[0]["ip"]
            
            # We update host interfaces
            api_call("host.update", {
                "hostid": host_id,
                "interfaces": [
                    {
                        "type": 2, # SNMP
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "161",
                        "details": {
                            "version": 2,
                            "bulk": 1,
                            "community": "{$SNMP_COMMUNITY}"
                        }
                    }
                ]
            }, auth=auth_token)
            print(f"Host '{h['name']}' updated to SNMP.")

print("\n=== All MikroTik hosts now use SNMP port 161! ===")
