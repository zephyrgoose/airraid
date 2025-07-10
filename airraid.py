#!/usr/bin/python3
# airraid.py

from bulk_accumulator import run_bulk_accumulator
from bulk_discriminator import process_wireless_data
from interface_manager import get_wireless_interfaces, select_wireless_interface
from monitor_mode import enable_monitor_mode, disable_monitor_mode
from handshake_capturer import capture_handshake

def main():
    networks, _ = run_bulk_accumulator()
    results = process_wireless_data()

    if not results:
        print("No networks with clients found.")
        return

    print("Available networks with clients:")
    for idx, net in enumerate(results):
        print(f"{idx + 1}. {net['ESSID']} ({net['station_mac']}) - {net['number_of_clients']} clients")

    try:
        selection = int(input("Select a network to capture handshake from: ")) - 1
        target = results[selection]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    interfaces = get_wireless_interfaces()
    interface = select_wireless_interface(interfaces)
    if interface is None:
        print("Error: No wireless interface selected")
        return

    mon_iface = enable_monitor_mode(interface)
    channel = None
    for n in networks['networks']:
        if n.get('BSSID', '').strip() == target['station_mac']:
            channel = n.get('channel') or n.get('Channel')
            break
    try:
        channel = int(channel)
    except (TypeError, ValueError):
        channel = 1

    try:
        capture_handshake(mon_iface, target['station_mac'], target['ESSID'], channel, 600)
    finally:
        disable_monitor_mode(mon_iface)

if __name__ == "__main__":
    main()
