from networkscanner import topology

def test_load_devices_from_json():
    json_data = '''
    {
        "192.168.1.1": {
            "host": "router",
            "macaddress": "AA:BB:CC:DD:EE:FF",
            "os_name": "Linux",
            "os_accuracy": "99",
            "router": true
        }
    }
    '''
    devices = topology.load_devices_from_json(json_data)
    assert isinstance(devices, dict)
    assert "192.168.1.1" in devices
    assert devices["192.168.1.1"]["host"] == "router"

def test_make_device_label():
    infos = {
        "host": "laptop",
        "macaddress": "11:22:33:44:55:66",
        "os_name": "Windows",
        "os_accuracy": "95"
    }
    label = topology.make_device_label("192.168.1.2", infos)
    assert "192.168.1.2" in label
    assert "laptop" in label
    assert "11:22:33:44:55:66" in label
    assert "Windows" in label
    assert "Accuracy: 95" in label

def test_create_network_graph():
    devices = {
        "192.168.1.1": {
            "host": "router",
            "macaddress": "AA:BB:CC:DD:EE:FF",
            "os_name": "Linux",
            "os_accuracy": "99",
            "router": True
        },
        "192.168.1.10": {
            "host": "laptop",
            "macaddress": "11:22:33:44:55:66",
            "os_name": "Windows",
            "os_accuracy": "95"
        }
    }
    G = topology.create_network_graph(devices)
    assert len(G.nodes) == 2
    assert len(G.edges) == 1

def test_draw_network_graph_no_save():
    devices = {
        "192.168.1.1": {
            "host": "router",
            "macaddress": "AA:BB:CC:DD:EE:FF",
            "os_name": "Linux",
            "os_accuracy": "99",
            "router": True
        },
        "192.168.1.10": {
            "host": "laptop",
            "macaddress": "11:22:33:44:55:66",
            "os_name": "Windows",
            "os_accuracy": "95"
        }
    }
    G = topology.create_network_graph(devices)
    plt = topology.draw_network_graph(G, save=False)
    assert plt is not None

def test_draw_network_graph_save(tmp_path):
    devices = {
        "192.168.1.1": {
            "host": "router",
            "macaddress": "AA:BB:CC:DD:EE:FF",
            "os_name": "Linux",
            "os_accuracy": "99",
            "router": True
        },
        "192.168.1.10": {
            "host": "laptop",
            "macaddress": "11:22:33:44:55:66",
            "os_name": "Windows",
            "os_accuracy": "95"
        }
    }
    G = topology.create_network_graph(devices)
    output_file = tmp_path / "test_graph.png"
    result = topology.draw_network_graph(G, filename=str(output_file), save=True)
    assert output_file.exists()
    assert result is None