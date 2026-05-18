import json
from networkscanner import nmap
from unittest.mock import patch, MagicMock

@patch("networkscanner.nmap.nmap3.NmapHostDiscovery")
def test_discover_hosts(mock_nmap_class):
    """Test the discover_hosts function to ensure it returns expected results."""
    mock_instance = MagicMock()
    mock_result = {
        "192.168.1.1": {
            "state": "up",
            "hostname": "router"
        },
        "192.168.1.10": {
            "state": "up",
            "hostname": "laptop"
        }
    }
    mock_instance.nmap_no_portscan.return_value = mock_result
    mock_nmap_class.return_value = mock_instance

    result = nmap.discover_hosts("192.168.1.0/24")

    assert result == mock_result
    mock_instance.nmap_no_portscan.assert_called_once_with("192.168.1.0/24")

@patch("networkscanner.nmap.nmap3.Nmap")
def test_detect_os(mock_nmap_class):
    """Test the detect_os function to ensure it returns expected results."""
    mock_instance = MagicMock()
    expected_result = {
        "192.168.1.50": {
            "osmatch": [
                {"name": "Linux 3.2 - 4.9", "accuracy": "98"},
                {"name": "FreeBSD", "accuracy": "80"}
            ]
        }
    }
    mock_instance.nmap_os_detection.return_value = expected_result
    mock_nmap_class.return_value = mock_instance

    result = nmap.detect_os("192.168.1.50")

    assert result == expected_result
    mock_instance.nmap_os_detection.assert_called_once_with("192.168.1.50")

def test_filter_results_by_state():
    """Test the filter_results_by_state function to ensure it filters results correctly."""
    input_data = {
        "192.168.1.1": {"state": {"state": "up"}},
        "192.168.1.2": {"state": {"state": "down"}},
        "192.168.1.3": {"state": {"state": "up"}},
        "192.168.1.4": {"something_else": "irrelevant"},
        "192.168.1.5": "not a dict"
    }

    expected_up = {
        "192.168.1.1": {"state": {"state": "up"}},
        "192.168.1.3": {"state": {"state": "up"}}
    }

    expected_down = {
        "192.168.1.2": {"state": {"state": "down"}}
    }

    result_up = nmap.filter_results_by_state(input_data)
    assert result_up == expected_up

    result_down = nmap.filter_results_by_state(input_data, state="down")
    assert result_down == expected_down


@patch("networkscanner.nmap.subprocess.check_output")
@patch("networkscanner.nmap.platform.system")
def test_get_default_ip_windows(mock_platform, mock_subproc):
    mock_platform.return_value = "Windows"
    mock_subproc.return_value = """
Interface List
  1...00 ff 36 12 2d 19 ......Intel(R) Ethernet
IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0       192.168.1.1     192.168.1.101     25
===========================================================================
"""
    result = nmap.get_default_ip()
    assert result == "192.168.1.1"


@patch("networkscanner.nmap.subprocess.check_output")
@patch("networkscanner.nmap.platform.system")
def test_get_default_ip_linux(mock_platform, mock_subproc):
    """Test the get_default_ip function for Linux systems."""
    mock_platform.return_value = "Linux"
    mock_subproc.return_value = "1.1.1.1 via 192.168.0.1 dev eth0 src 192.168.0.100 uid 1000\n"
    result = nmap.get_default_ip()
    assert result == "192.168.0.1"


@patch("networkscanner.nmap.subprocess.check_output")
@patch("networkscanner.nmap.platform.system")
def test_get_default_ip_macos_fallback(mock_platform, mock_subproc):
    """Test the get_default_ip function for macOS systems with fallback."""
    mock_platform.return_value = "Darwin"

    def side_effect(cmd, *args, **kwargs):
        if isinstance(cmd, list) and cmd[0] == "ip":
            raise FileNotFoundError("ip not found")
        else:
            return "   gateway: 192.168.1.254\n"

    mock_subproc.side_effect = side_effect
    result = nmap.get_default_ip()
    assert result == "192.168.1.254"

@patch("networkscanner.nmap.detect_os")
@patch("networkscanner.nmap.get_default_ip")
@patch("networkscanner.nmap.filter_results_by_state")
def test_merge_host_os_info(mock_filter, mock_gateway, mock_os_detect):
    """Test the merge_host_os_info function to ensure it merges host and OS info correctly."""
    sample_hosts = {
        "192.168.1.10": {
            "hostname": [{"name": "host-A"}],
            "macaddress": {"addr": "AA:BB:CC:DD:EE:FF"},
            "state": {"state": "up"}
        },
        "192.168.1.1": {
            "hostname": [{"name": "router"}],
            "macaddress": {"addr": "11:22:33:44:55:66"},
            "state": {"state": "up"}
        }
    }

    mock_filter.return_value = sample_hosts
    mock_gateway.return_value = "192.168.1.1"
    mock_os_detect.side_effect = lambda ip: {
        ip: {
            "osmatch": [{"name": f"Linux for {ip}", "accuracy": "95"}]
        }
    }

    result = nmap.merge_host_os_info(sample_hosts)
    result_dict = json.loads(result)

    assert "192.168.1.10" in result_dict
    assert "192.168.1.1" in result_dict

    assert result_dict["192.168.1.10"]["host"] == "host-A"
    assert result_dict["192.168.1.10"]["macaddress"] == "AA:BB:CC:DD:EE:FF"
    assert result_dict["192.168.1.10"]["os_name"] == "Linux for 192.168.1.10"
    assert result_dict["192.168.1.10"]["os_accuracy"] == "95"
    assert "router" not in result_dict["192.168.1.10"]

    assert result_dict["192.168.1.1"]["router"] is True