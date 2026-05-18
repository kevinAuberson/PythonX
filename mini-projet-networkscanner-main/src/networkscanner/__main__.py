import click
from . import nmap
from . import topology

@click.command()
@click.option('--ipaddress', default='192.168.150.0/24')
def main(ipaddress):
    """
    Discover hosts on the network and visualize the topology.
    :param ipaddress: The IP address range to scan (default value set for Docker network: 192.168.150.0/24)
    """
    hosts = nmap.discover_hosts(ipaddress)
    json_results = nmap.merge_host_os_info(hosts)
    print(json_results)

    devices = topology.load_devices_from_json(json_results)
    G = topology.create_network_graph(devices)
    topology.draw_network_graph(G)

if __name__ == "__main__":
    main()
