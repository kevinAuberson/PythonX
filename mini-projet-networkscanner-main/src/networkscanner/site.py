import streamlit as st
import re
import nmap
import topology
import pandas as pd
from io import StringIO
import io

st.write("""
# Network Scanner
This is the site page of the Network Scanner application.""")

ip_with_mask_pattern = r'^((25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(25[0-5]|2[0-4]\d|1?\d{1,2})\/([0-9]|[1-2][0-9]|3[0-2])$'

result= None

@st.fragment
def download_json(data, filename):
    """
    Function to download JSON data as a file.
    """
    st.download_button(
        label="Download JSON",
        data=data,
        file_name=filename,
        mime='application/json'
    )

@st.fragment
def download_image(plt, filename):
    """
    Function to download the network graph image.
    """
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    st.download_button(
        label="Download Network Graph",
        data=buffer,
        file_name=filename,
        mime='image/png'
    )

with st.form("ip_form"):
    """
    ## Network Scanner Form
    This form allows you to scan your network for devices.
    Enter your network IP address with the mask (e.g., 192.168.1.0/24)
    """
    st.subheader("Network IP")
    st.write("Please enter your IP address with the mask")
    ip_address = st.text_input("Enter your network address with the mask (e.g., 192.168.1.0/24)")
    submitted = st.form_submit_button("Scan")

    if submitted:
        if re.fullmatch(ip_with_mask_pattern, ip_address):
            st.success(f"Scanning IP: {ip_address}")
            result = nmap.merge_host_os_info(nmap.discover_hosts(ip_address))

            if result:
                df = pd.read_json(StringIO(result), orient='index')
                st.write("### Scan Result:")
                st.dataframe(df)
                devices = topology.load_devices_from_json(result)
                G = topology.create_network_graph(devices)
                plt = topology.draw_network_graph(G, save=False)
                st.write("### Network Graph:")
                st.pyplot(plt)
            else:
                st.warning("No hosts found or scan failed.")
        else:
            st.error("Invalid IP address format. Please use format like 192.168.1.1/24.")

if result is not None:
    st.subheader("Download Results")
    st.write("You can download the scan results as a JSON file or PNG.")

    download_json(data=result, filename='scan_results.json')

    download_image(plt=plt, filename='network.png')