Overview

This project is a complete system for scanning networks, sending device data to a cloud dashboard, and visualizing network topology using PyVis.

It consists of:

Flask Web Dashboard (hosted on Linux server)

Network Map Generator using PyVis

Windows Agent Scanner (EXE) built with Nmap + Python

Secure API endpoint (/agent_report) for sending device data

Apache front-end with embedded AdminLTE UI

Systemd service to run Flask automatically


Features:

Web Dashboard

Displays PyVis-generated interactive network maps

Live updates from agent reports

Supports subnet & gateway manual scans

AdminLTE interface (Bootstrap 5, responsive)


Windows Agent (EXE)

Uses portable Nmap for host discovery

Does NOT require installation or admin rights

Reads configuration (subnet, endpoint, API key) from config.txt

Sends device data (IP, MAC, hostname) to the server

Packaged using PyInstaller in a portable ZIP


Secure Agent API

Authentication via shared AGENT_API_KEY

Stores results in /opt/network_dashboard/agent_reports/latest.json

Supports multiple scans & future multi-agent setups

Backend Components

Flask app with app.run(host="0.0.0.0", port=5000)

Systemd-managed service for reliable startup

Apache server hosting static dashboard & agent downloads

Project Structure
/opt/network_dashboard/
│── app.py                     # Main Flask app
│── venv/                      # Python virtual environment
│── templates/
│     ├── dashboard.html       # AdminLTE dashboard
│     ├── form.html
│── /var/www/html/
│     ├── network_map.html     # Auto-generated PyVis map
│── agent_reports/
│     └── latest.json          # Last agent scan


Windows EXE download:

/var/www/html/agents/
    NetworkScannerAgent.zip

How It Works
1. User Runs Agent on Windows

The agent:

Loads config.txt

Runs Nmap (nmap.exe -sn <subnet>)

Parses results

Sends JSON to /agent_report

Example payload:

{
  "api_key": "YOUR_KEY",
  "subnet": "192.168.2.0/24",
  "devices": [
    {"ip": "192.168.2.10", "hostname": "PC1", "mac": "AA:BB:CC:DD:EE:FF"}
  ]
}

2. Server Receives the Report

Flask route:

@app.route("/agent_report", methods=["POST"])


Validates API key

Saves latest.json

Updates in-memory latest_report

Used by dashboard & map generator

3. Dashboard Displays Devices

Loads latest.json

Renders a summary table

Creates an interactive PyVis map with nodes

4. Map Generator Creates map

The server writes a fresh:

/var/www/html/network_map.html


The dashboard iframe loads it with cache-busting:

<iframe src="network_map.html?v={{ random() }}"></iframe>

🔧 Installation Instructions (Server)
1. Clone or copy project
sudo mkdir -p /opt/network_dashboard
cd /opt/network_dashboard
# copy project files here

2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install flask pyvis

3. Create agent report directory
sudo mkdir -p /opt/network_dashboard/agent_reports
sudo chown -R www-data:www-data /opt/network_dashboard

4. Enable systemd service

/etc/systemd/system/network_dashboard.service:

[Unit]
Description=Flask PyVis Network Map Generator
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/network_dashboard
Environment="PATH=/opt/network_dashboard/venv/bin"
ExecStart=/opt/network_dashboard/venv/bin/python3 /opt/network_dashboard/app.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


Enable:

sudo systemctl daemon-reload
sudo systemctl enable network_dashboard.service
sudo systemctl restart network_dashboard.service

Installation Instructions (Windows Agent)
1. Download ZIP from dashboard

http://YOUR_SERVER/agents/NetworkScannerAgent.zip

2. Extract contents

Ensure directory contains:

one_time_scan.exe
config.txt
nmap_portable/

3. Edit config.txt
subnet=192.168.2.0/24
endpoint=http://YOUR_SERVER_IP:5000/agent_report
api_key=YOUR_KEY

4. Run the EXE

The EXE will:

Scan the network

Send results to the server

Print detailed output


Security Notes

API key is required for any agent to send data

Endpoint only accepts POST JSON

Apache serves only static files

Flask handles sensitive data separately

Future: optional JWT or HTTPS mutual auth


Troubleshooting
EXE error: “actively refused connection”

Server not listening on port 5000
→ Run:

sudo ss -tulpn | grep 5000


Must show:

0.0.0.0:5000


Server error: NameError: API_KEY

You used API_KEY instead of AGENT_API_KEY.


Map not updating

Browser caching → add "?v={{ random() }}" to iframe.

