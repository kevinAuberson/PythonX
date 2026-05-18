import subprocess
import nmap3
import json
import platform

def discover_hosts(target):
    """
    Discover hosts on the given network or IP using nmap's no-portscan mode.

    Parameters:
        target (str): IP address or network in CIDR format (e.g., "192.168.1.0/24").

    Returns:
        dict: Dictionary where keys are discovered IPs and values are host information.
    """
    host_discovery = nmap3.NmapHostDiscovery()
    return host_discovery.nmap_no_portscan(target)
     
def detect_os(ip):
    """
    Detect the operating system for a given IP address using nmap.

    Parameters:
        ip (str): Target IP address.

    Returns:
        dict: Raw OS detection result, usually {ip: {...}}.
    """
    os_scan = nmap3.Nmap()
    return os_scan.nmap_os_detection(ip) 

def filter_results_by_state(results_dict, state="up"):
    """
    Filter discovered hosts by their state (default: 'up').

    Parameters:
        results_dict (dict): Result from discover_hosts().
        state (str): Desired state ('up', 'down', etc.).

    Returns:
        dict: Filtered dictionary containing only hosts in the desired state.
    """
    return {
        ip: data
        for ip, data in results_dict.items()
        if isinstance(data, dict) and data.get('state', {}).get('state') == state
    }

def get_default_ip():
    """
    Get the default gateway IP address in a cross-platform way.

    Returns:
        str: The default gateway IP address as a string.
    """
    system = platform.system()
    if system == "Windows":
        output = subprocess.check_output("route print 0.0.0.0", shell=True, universal_newlines=True)
        for line in output.splitlines():
            if line.strip().startswith("0.0.0.0"):
                parts = line.split()
                if len(parts) >= 3:
                    return parts[2]
    else:
        try:
            output = subprocess.check_output(["ip", "route", "get", "1.1.1.1"], universal_newlines=True)
            return output.split(" ")[2]
        except Exception:
            # Fallback for macOS or systems without 'ip'
            output = subprocess.check_output("route -n get default", shell=True, universal_newlines=True)
            for line in output.splitlines():
                if "gateway:" in line:
                    return line.split()[-1]
    return ""

def merge_host_os_info(hosts):
    """
    Merge host discovery and OS detection results, keeping only useful information.

    Parameters:
        hosts (dict): The result from discover_hosts(), where each key is an IP address
                      and each value is a dictionary with host information.

    Returns:
        str: A JSON-formatted string where each key is an IP address and each value is a dictionary
             containing the hostname, MAC address, OS name, and OS accuracy.
    """
    merged_results = {}
    up_hosts = filter_results_by_state(hosts)
    gateway_ip = get_default_ip()
    for ip, data in up_hosts.items():
        os_result = detect_os(ip)
        hostname = ""
        hostname_list = data.get('hostname', [])
        if hostname_list :
            hostname = hostname_list[0].get('name', '')
        mac = data.get('macaddress', '')
        if isinstance(mac, dict):
            mac = mac.get('addr', '')
        os_name = ""
        os_accuracy = ""
        host_os_info = os_result.get(ip, {})
        osmatches = host_os_info.get('osmatch', [])
        if osmatches:
            os_name = osmatches[0].get('name', '')
            os_accuracy = osmatches[0].get('accuracy', '')
        host_info = {
            "host": hostname,
            "macaddress": mac,
            "os_name": os_name,
            "os_accuracy": os_accuracy
        }
        if ip == gateway_ip:
            host_info["router"] = True
        merged_results[ip] = host_info
    return json.dumps(merged_results, indent=2)