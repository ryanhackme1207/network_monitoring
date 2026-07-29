# MikroTik Network Telemetry & Alert Dashboard

A dedicated, real-time web application connected to your **Zabbix 7.0 LTS engine** to monitor all MikroTik router interfaces, latency, and ethernet down alerts.

## 🚀 Live Dashboard Web App

- **Dashboard Web URL**: [http://localhost:3000](http://localhost:3000)
- **Zabbix Native Admin**: [http://localhost:8080](http://localhost:8080) (User: `Admin` | Password: `zabbix`)

---

## 📡 Monitored Router Interfaces

| Interface | IP Address | Purpose / Type | Zabbix Status |
| :--- | :--- | :--- | :--- |
| **`ether4`** | `192.168.30.1` | Default Subnet Gateway (VLAN 30) | 🟢 ONLINE (SNMP & ICMP) |
| **`ether1`** | `192.168.31.219` | Primary Internet WAN Gateway | 🟢 ONLINE (ICMP Ping) |
| **`ether2`** | `192.168.10.1` | 802.1x Authentication Network | 🟢 ONLINE (ICMP Ping) |
| **`ether5`** | `10.40.40.1` | PPPoE Server Network Interface | 🟢 ONLINE (ICMP Ping) |
| **`bridge`** | `192.168.50.1` | Main RouterOS Bridge Interface | 🟢 ONLINE (ICMP Ping) |

---

## ⚡ Dashboard Features

1. **Interface Situation Matrix**: Real-time status cards showing latency, packet loss, and link health for all 5 router interfaces.
2. **Real-Time Alert Feed & Toast Notifications**: Displays active Zabbix trigger alerts instantly. Shows glowing red alert toasts when any ethernet port goes DOWN.
3. **Outage Simulation Tool**: Includes a top-bar **"Simulate Interface Down"** button to test and preview real-time link down alert popups.
4. **Live Latency Graph**: Interactive Chart.js graph plotting sub-millisecond response times.
