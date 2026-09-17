# Screenshots & Visual Assets Guide

This directory holds architecture diagrams, topology schemas, and UI screenshots for the **Astra SIEM & SOAR** project.

Below is the list of expected images referenced in `README.md` and `README_RU.md`:

| Filename | Description | Source / Recommendation |
|---|---|---|
| `architecture_diagram.png` | System architecture & 3-tier network topology (Sensors, DMZ Gateway, Core) | Schema from presentation slide 10 / Figure 3.1 in thesis |
| `soar_dashboard.png` | SOAR Master Console: ML agent status, active controls, and anomaly alert feed | Screenshot of the Vue.js Dashboard view (`http://localhost:5173/`) |
| `sensor_inventory.png` | Sensor Management: Sensor table, live telemetry (CPU/RAM), status indicators | Screenshot of Sensors view (`http://localhost:5173/sensors`) |
| `suricata_rules_git.png` | IDS Rules Management: Custom rules table, batch deploy modal, Git sync | Screenshot of Rules view (`http://localhost:5173/rules`) |
| `vpn_pki_management.png` | OpenVPN & PKI Management: Client profiles, serial numbers, revocation | Screenshot of VPN view (`http://localhost:5173/vpn`) |
| `pcap_traffic_capture.png` | Traffic Records: Remote PCAP capture listing, download controls | Screenshot of PCAP view (`http://localhost:5173/pcap`) |
| `kibana_investigation.png` | Kibana Discover view opened via dynamic deep link ($\pm 5$ min time window) | Screenshot of Kibana Discover with highlighted anomaly event |
| `queuing_theory_chart.png` | Latency vs Load graph ($T_{centr}$ vs $T_{MAS}$) from Queuing Theory analysis | Chart from presentation slide 11 / Figure 4.1 in thesis |

> **Note:** The Markdown documentation includes SVG/text fallback schemas and graceful formatting if screenshots have not yet been copied into this folder.
