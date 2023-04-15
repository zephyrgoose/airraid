from scapy.all import *
from collections import defaultdict
import os
import subprocess
import sys

def get_wifi_interfaces():
    """
    Get a list of available Wi-Fi interfaces.
    :return: A list of Wi-Fi interface names
    """
    interfaces = os.listdir('/sys/class/net')
    wifi_interfaces = [iface for iface in interfaces if 'wlan' in iface]
    return wifi_interfaces

def enable_monitor_mode(interface):
    """
    Enable monitor mode on the given Wi-Fi interface.
    :param interface: The Wi-Fi interface's name
    :return: The monitor mode interface's name or None if unsuccessful
    """
    try:
        subprocess.run(["sudo", "ifconfig", interface, "down"], check=True)
        subprocess.run(["sudo", "iwconfig", interface, "mode", "monitor"], check=True)
        subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)
        return interface
    except subprocess.CalledProcessError:
        return None

def disable_monitor_mode(interface):
    """
    Disable monitor mode on the given Wi-Fi interface.
    :param interface: The Wi-Fi interface's name
    """
    subprocess.run(["sudo", "ifconfig", interface, "down"], check=True)
    subprocess.run(["sudo", "iwconfig", interface, "mode", "managed"], check=True)
    subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)

def sniff_wifi_packets(packet_callback, interface, timeout=60):
    """
    Sniffs for Wi-Fi packets and calls the provided callback function for each packet.
    :param packet_callback: The callback function to be executed for each packet
    :param interface: The Wi-Fi interface's name
    :param timeout: The duration (in seconds) to sniff for packets
    """
    sniff(iface=interface, prn=packet_callback, timeout=timeout, store=0)

def handle_packet(packet):
    """
    Handles packets captured by the sniffer and prints access point information.
    :param packet: The packet captured by the sniffer
    """
    if packet.haslayer(Dot11Beacon):
        bssid = packet[Dot11].addr2
        ssid = packet[Dot11Elt].info.decode()
        channel = int(ord(packet[Dot11Elt:3].info))
        print(f"SSID: {ssid}, BSSID: {bssid}, Channel: {channel}")

def main():
    wifi_interfaces = get_wifi_interfaces()
    if not wifi_interfaces:
        print("No Wi-Fi interfaces found.")
        sys.exit(1)

    print("Available Wi-Fi interfaces:")
    for idx, iface in enumerate(wifi_interfaces):
        print(f"{idx + 1}. {iface}")

    selected_idx = int(input("Select an interface to use (enter the number): ")) - 1
    if selected_idx < 0 or selected_idx >= len(wifi_interfaces):
        print("Invalid selection. Exiting.")
        sys.exit(1)

    selected_iface = wifi_interfaces[selected_idx]
    print(f"Enabling monitor mode on {selected_iface}...")
    monitor_iface = enable_monitor_mode(selected_iface)
    if not monitor_iface:
        print("Failed to enable monitor mode. Exiting.")
        sys.exit(1)

    print("Monitor mode enabled. Starting Wi-Fi scan...")
    try:
        sniff_wifi_packets(handle_packet, monitor_iface)
    finally:
        print("Disabling monitor mode...")
        disable_monitor_mode(monitor_iface)
        print("Scan complete.")

if __name__ == "__main__":
    main()

