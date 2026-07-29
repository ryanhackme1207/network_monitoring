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
auth_token = login_res["result"]
print("Logged into Zabbix API.")

# 2. Update or Create MikroTik-hEX host
existing = api_call("host.get", {"filter": {"host": ["MikroTik-hEX", "MikroTik-Router"]}}, auth=auth_token)["result"]
host_id = None

if existing:
    host_id = existing[0]["hostid"]
    print(f"Updating host ID {host_id} name to MikroTik-hEX...")
    api_call("host.update", {
        "hostid": host_id,
        "host": "MikroTik-hEX",
        "name": "MikroTik-hEX"
    }, auth=auth_token)
else:
    print("Creating host MikroTik-hEX...")
    res = api_call("host.create", {
        "host": "MikroTik-hEX",
        "name": "MikroTik-hEX",
        "interfaces": [{
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
        }],
        "groups": [{"groupid": "5"}],
        "templates": [{"templateid": "10233"}] # Mikrotik by SNMP
    }, auth=auth_token)
    host_id = res["result"]["hostids"][0]

print(f"MikroTik-hEX host ID: {host_id}")

# 3. Check items on host
items = api_call("item.get", {"hostids": [host_id], "output": ["itemid", "name", "key_", "lastvalue"]}, auth=auth_token)["result"]
print(f"Total items on MikroTik-hEX: {len(items)}")

cpu_item = next((i for i in items if "cpu" in i["name"].lower() or "processor" in i["name"].lower()), None)
uptime_item = next((i for i in items if "uptime" in i["name"].lower()), None)
mem_item = next((i for i in items if "memory" in i["name"].lower()), None)
traffic_in_item = next((i for i in items if "bits received" in i["name"].lower() or "incoming" in i["name"].lower()), None)
traffic_out_item = next((i for i in items if "bits sent" in i["name"].lower() or "outgoing" in i["name"].lower()), None)

print("\n--- Key Metrics Identified ---")
print("CPU Item:", cpu_item["name"] if cpu_item else "N/A")
print("Memory Item:", mem_item["name"] if mem_item else "N/A")
print("Uptime Item:", uptime_item["name"] if uptime_item else "N/A")
print("Traffic In Item:", traffic_in_item["name"] if traffic_in_item else "N/A")
print("Traffic Out Item:", traffic_out_item["name"] if traffic_out_item else "N/A")

# 4. Check if Dashboard 'My Home Network Status' already exists
dashboards = api_call("dashboard.get", {"filter": {"name": ["My Home Network Status"]}}, auth=auth_token)["result"]

widgets = [
    {
        "type": "hostavail",
        "name": "MikroTik hEX Availability & Health",
        "x": 0,
        "y": 0,
        "width": 12,
        "height": 4,
        "fields": [
            {"type": 2, "name": "groupids.0", "value": "5"}
        ]
    },
    {
        "type": "svggraph",
        "name": "WAN / LAN Traffic (ether1 & vlan30)",
        "x": 0,
        "y": 4,
        "width": 12,
        "height": 6,
        "fields": [
            {"type": 1, "name": "ds.0.hosts.0", "value": "MikroTik-hEX"},
            {"type": 1, "name": "ds.0.items.0", "value": "Interface ether1*: Bits sent"},
            {"type": 1, "name": "ds.0.color", "value": "00F0FF"},
            {"type": 1, "name": "ds.1.hosts.0", "value": "MikroTik-hEX"},
            {"type": 1, "name": "ds.1.items.0", "value": "Interface ether1*: Bits received"},
            {"type": 1, "name": "ds.1.color", "value": "10B981"}
        ]
    },
    {
        "type": "svggraph",
        "name": "CPU Load & Utilization",
        "x": 0,
        "y": 10,
        "width": 12,
        "height": 5,
        "fields": [
            {"type": 1, "name": "ds.0.hosts.0", "value": "MikroTik-hEX"},
            {"type": 1, "name": "ds.0.items.0", "value": "*CPU*"},
            {"type": 1, "name": "ds.0.color", "value": "FF3366"}
        ]
    }
]

if dashboards:
    dash_id = dashboards[0]["dashboardid"]
    print(f"Updating existing Dashboard ID {dash_id}...")
    api_call("dashboard.update", {
        "dashboardid": dash_id,
        "name": "My Home Network Status",
        "pages": [{"widgets": widgets}]
    }, auth=auth_token)
else:
    print("Creating new Zabbix Dashboard 'My Home Network Status'...")
    res = api_call("dashboard.create", {
        "name": "My Home Network Status",
        "pages": [{"widgets": widgets}]
    }, auth=auth_token)
    print("Create Dashboard result:", res.get("result"))

print("\nALL 4 STEPS COMPLETED SUCCESSFULLY!")
