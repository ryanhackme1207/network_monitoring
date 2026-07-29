# Zabbix Network Monitoring Setup Guide

Your Zabbix 7.0 LTS monitoring server is fully deployed and running in Docker!

## 🚀 Quick Access

- **Web Dashboard**: [http://localhost:8080](http://localhost:8080)
- **Default Username**: `Admin`
- **Default Password**: `zabbix` *(Change password after initial login!)*

---

## 🛠️ Step-by-Step: Adding Network Devices to Monitor

### 1. Monitor Any Network Device via Ping (ICMP)
*Ideal for IP cameras, printers, unmanaged switches, access points, or basic uptime tracking.*

1. Log into Zabbix at [http://localhost:8080](http://localhost:8080).
2. Go to **Data collection** ➔ **Hosts**.
3. Click the **Create host** button (top right).
4. Fill in the host details:
   - **Host name**: `Main-Router` (or any friendly name).
   - **Templates**: Search and select `ICMP Ping`.
   - **Host groups**: Select `Templates/Network devices` or `Discovered hosts`.
   - **Interfaces**: Click **Add** ➔ Select **Agent**.
     - Set **IP address** to your target device's IP (e.g., `192.168.88.1`).
     - Set **Port** to `10050`.
5. Click **Add** at the bottom.
6. *Zabbix will now ping the device every minute and alert you if packet loss occurs or latency spikes.*

---

### 2. Monitor Routers & Switches via SNMP (MikroTik, Cisco, TP-Link, etc.)
*Ideal for bandwidth usage, interface status (up/down), CPU/RAM utilization, and link speed.*

#### Step A: Enable SNMP on your Network Device (Example: MikroTik)
In MikroTik WinBox / Terminal:
```routeros
/snmp set enabled=yes contact="Admin" location="ServerRoom"
/snmp community add name=public addresses=0.0.0.0/0 read-access=yes
```

#### Step B: Configure Host in Zabbix
1. Go to **Data collection** ➔ **Hosts** ➔ Click **Create host**.
2. **Host name**: `MikroTik-Gateway`
3. **Templates**: Search and select one of:
   - `MikroTik by SNMP` *(For MikroTik routers/switches)*
   - `Network Generic Device by SNMP` *(For generic switches/routers)*
4. **Interfaces**: Click **Add** ➔ Select **SNMP**.
   - **IP address**: Device IP (e.g., `192.168.88.1`)
   - **Port**: `161`
   - **SNMP version**: `SNMPv2`
   - **SNMP community**: `{$SNMP_COMMUNITY}` (Defaults to `public`).
5. **Macros Tab**:
   - If your community name is different from `public`, click **Inherited and host macros**, locate `{$SNMP_COMMUNITY}`, and change value to your secret string (e.g. `my_snmp_pass`).
6. Click **Add**.

---

### 3. Viewing Live Traffic Graphs & Alerts

- **Live Bandwidth Graphs**:
  Go to **Monitoring** ➔ **Hosts** ➔ Click on your device ➔ Click **Graphs** or **Latest data** to see real-time interface traffic (bits/sec in vs out).
- **Problems & Alerts**:
  Go to **Monitoring** ➔ **Problems** to view current active issues (e.g. interface down, high ping latency, router reboot).

---

## ⚡ Useful Powershell Commands

| Action | Command |
| :--- | :--- |
| **Check Status** | `.\manage-zabbix.ps1 status` |
| **Start Zabbix** | `.\manage-zabbix.ps1 start` |
| **Stop Zabbix** | `.\manage-zabbix.ps1 stop` |
| **View Server Logs**| `.\manage-zabbix.ps1 logs` |

---

> [!TIP]
> **Need to monitor remote networks or devices behind NAT?**
> You can deploy a lightweight **Zabbix Proxy** Docker container on the remote site to collect data and forward it back to this Zabbix Server securely!
