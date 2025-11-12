import nmap
import socket
from pyvis.network import Network

# Settings
SUBNET = "192.168.1.0/24"   # Change to your lab subnet
GATEWAY = "192.168.1.1"     # Change to your router/gateway IP
OUTPUT_FILE = "topology.html"

def reverse_dns(ip):
    """Try to resolve hostname from IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

def scan_network(subnet):
    """Run Nmap ping sweep on a subnet."""
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments="-sn")
    hosts = []
    for host in nm.all_hosts():
        if nm[host].state() == "up":
            hostname = nm[host].hostname() or reverse_dns(host) or "Unknown"
            mac = nm[host]['addresses'].get('mac', 'N/A')
            hosts.append({
                "ip": host,
                "hostname": hostname,
                "mac": mac
            })
    return hosts

def build_topology(hosts, gateway, output_file):
    """Build an interactive network map."""
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.force_atlas_2based()

    # Add gateway
    net.add_node(gateway, label=f"Gateway ({gateway})", color="red", shape="star")

    # Add other hosts
    for host in hosts:
        if host["ip"] == gateway:
            continue
        label = f"{host['hostname']}\n{host['ip']}\n{host['mac']}"
        net.add_node(host["ip"], label=label, color="lightblue", shape="ellipse")
        net.add_edge(gateway, host["ip"])

    # Generate output
    net.show(output_file)
    print(f"[+] Topology map saved to {output_file}")

if __name__ == "__main__":
    print(f"[+] Scanning subnet {SUBNET} ...")
    hosts = scan_network(SUBNET)
    print(f"[+] Found {len(hosts)} active hosts")
    build_topology(hosts, GATEWAY, OUTPUT_FILE)
