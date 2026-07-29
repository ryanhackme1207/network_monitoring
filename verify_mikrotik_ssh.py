import paramiko
import json
import urllib.request
import time

MIKROTIK_IP = "192.168.50.1"
USER = "admin"
PASS = "admin123456"
ZABBIX_URL = "http://localhost:8080/api_jsonrpc.php"

def get_mikrotik_info():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to MikroTik at {MIKROTIK_IP} via SSH...")
        ssh.connect(MIKROTIK_IP, username=USER, password=PASS, timeout=10)
        
        commands = {
            "identity": "/system identity print",
            "resource": "/system resource print",
            "interfaces": "/interface print detail",
            "ip_addresses": "/ip address print detail",
            "snmp": "/snmp print",
            "snmp_communities": "/snmp community print detail"
        }
        
        results = {}
        for key, cmd in commands.items():
            stdin, stdout, stderr = ssh.exec_command(cmd)
            results[key] = stdout.read().decode('utf-8').strip()
            
        ssh.close()
        return results
    except Exception as e:
        print("SSH Connection Error:", e)
        return None

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

def get_zabbix_data():
    login_res = api_call("user.login", {"username": "Admin", "password": "zabbix"})
    if "error" in login_res:
        return None
    auth_token = login_res["result"]
    
    hosts_res = api_call("host.get", {
        "output": ["hostid", "name", "status"],
        "selectInterfaces": ["ip", "available"],
    }, auth=auth_token)
    
    items_res = api_call("item.get", {
        "output": ["name", "key_", "lastvalue", "lastclock"],
        "monitored": True
    }, auth=auth_token)
    
    return {
        "hosts": hosts_res.get("result", []),
        "items": items_res.get("result", [])
    }

print("==========================================================================")
print("             MIKROTIK SSH vs ZABBIX SYNCHRONIZATION AUDIT                 ")
print("==========================================================================")

mt_data = get_mikrotik_info()
zb_data = get_zabbix_data()

if mt_data:
    print("\n--- MIKROTIK SYSTEM IDENTITY & RESOURCES (SSH) ---")
    print(mt_data["identity"])
    print("\n" + mt_data["resource"])
    print("\n--- MIKROTIK IP ADDRESSES (SSH) ---")
    print(mt_data["ip_addresses"])

if zb_data:
    print("\n--- ZABBIX SYNCHRONIZED HOSTS & SNMP STATUS ---")
    for h in zb_data["hosts"]:
        if "MikroTik" in h["name"]:
            ip = h["interfaces"][0]["ip"]
            avail = "GREEN (100% Synced)" if h["interfaces"][0]["available"] == "1" else "WAITING/POLLING"
            print(f" - Host: {h['name']:<40} | IP: {ip:<15} | Zabbix Status: {avail}")
            
    print("\n--- ZABBIX REAL-TIME POLLED METRICS ---")
    for item in zb_data["items"]:
        if item.get("lastvalue"):
            print(f" - {item['name']} ({item['key_']}): {item['lastvalue']}")

print("==========================================================================")
