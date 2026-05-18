import json
import networkx as nx
import matplotlib.pyplot as plt


def load_devices_from_json(json_data):
    """
    Load devices information from a JSON-formatted string.

    Parameters:
        json_data (str): JSON string representing the devices.

    Returns:
        dict: Dictionary where each key is an IP address and each value is a dictionary of device info.
    """
    return json.loads(json_data)

def create_network_graph(devices_json):
    """
    Create a NetworkX graph from the devices dictionary.
    The router (with "router": True) is set as the central node.

    Parameters:
        devices_json (dict): Dictionary with IPs as keys and device info as values.

    Returns:
        networkx.Graph: The constructed network graph with devices and router.
    """
    G = nx.Graph()
    router_ip = None
    router_label = "router\n"
    for ip, infos in devices_json.items():
        if infos.get("router"):
            router_ip = ip
            router_label = router_label + make_device_label(ip, infos)
            G.add_node(router_label, type='central')
            break

    for ip, infos in devices_json.items():
        if ip != router_ip:
            label = make_device_label(ip,infos)
            G.add_node(label, type='device')
            G.add_edge(router_label, label)

    return G

def make_device_label(ip, infos):
    """
    Create a label string for a network device node.

    Parameters:
        ip (str): The IP address of the device.
        infos (dict): Dictionary with keys like 'host', 'macaddress', 'os_name', 'os_accuracy'.

    Returns:
        str: A formatted label for the node.
    """
    host = infos.get('host', '') or '(no host)'
    mac = infos.get('macaddress', '') or '(no mac)'
    os_name = infos.get('os_name', '') or '(no os)'
    os_accuracy = infos.get('os_accuracy', '') or '(no accuracy)'
    return f"{ip}\n{host}\n{mac}\n{os_name}\nAccuracy: {os_accuracy}"

def draw_network_graph(G, filename='network.png', save=True):
    """
    Draw and save the network graph using matplotlib.

    Parameters:
        G (networkx.Graph): The network graph to draw.
        filename (str): The filename to save the image as (default: 'network.png').
        save (bool): If True, saves the image to file. If False, returns the matplotlib plt object.

    Returns:
        None or matplotlib.pyplot: None if saved, plt object if not.
    """
    pos = nx.spring_layout(G, k=0.5, seed=42)

    node_colors = ['red' if node == 'Routeur' else 'lightblue' for node in G.nodes()]

    plt.figure(figsize=(18, 12)) 
    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=3500, edge_color='gray', linewidths=1.5)

    labels = nx.get_node_attributes(G, 'label')

    for node, (x, y) in pos.items():
        label = labels.get(node, node)  
        plt.text(x, y, label, fontsize=11, fontweight='bold', ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.4'))

    plt.axis('off')
    if save:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print(f"Graph saved as {filename}")
        return None
    else:
        return plt

