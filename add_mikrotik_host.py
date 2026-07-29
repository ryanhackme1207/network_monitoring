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

# 1. Login
login_res = api_call("user.login", {"username": "Admin", "password": "zabbix"})
if "error" in login_res:
    print("Login error:", login_res["error"])
    exit(1)

auth_token = login_res["result"]
print("Logged in successfully. Token:", auth_token)

# 2. Check if host already exists
host_res = api_call("host.get", {"filter": {"host": ["MikroTik-Router"]}}, auth=auth_token)
if host_res.get("result"):
    print("Host MikroTik-Router already exists. Updating...")
    host_id = host_res["result"][0]["hostid"]
    update_res = api_call("host.update", {
        "hostid": host_id,
        "name": "MikroTik Router",
        "status": 0,
    }, auth=auth_token)
    print("Update result:", update_res)
else:
    # 3. Create host
    create_res = api_call("host.create", {
        "host": "MikroTik-Router",
        "name": "MikroTik Router",
        "interfaces": [
            {
                "type": 2, # SNMP
                "main": 1,
                "useip": 1,
                "ip": "192.168.30.1",
                "dns": "",
                "port": "161",
                "details": {
                    "version": 2,
                    "bulk": 1,
                    "community": "{$SNMP_COMMUNITY}"
                }
            }
        ],
        "groups": [
            {"groupid": "5"} # Discovered hosts
        ],
        "templates": [
            {"templateid": "10233"} # Mikrotik by SNMP
        ],
        "macros": [
            {
                "macro": "{$SNMP_COMMUNITY}",
                "value": "public"
            }
        ]
    }, auth=auth_token)
    print("Create result:", json.dumps(create_res, indent=2))
