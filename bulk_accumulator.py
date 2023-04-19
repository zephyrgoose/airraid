import json
from monitor_mode import enable_monitor_mode, disable_monitor_mode
from interface_manager import get_wireless_interfaces, select_wireless_interface
from bulk_accumulator_functions import get_capture_duration, capture_wireless_networks, parse_airodump_csv, get_metrics, print_metrics

def run_bulk_accumulator():
    interfaces = get_wireless_interfaces()
    interface_name = select_wireless_interface(interfaces)

    if interface_name is None:
        print("Error: No wireless interface selected")
        return

    capture_duration = get_capture_duration()
    output_file = "wireless_bulk.json"

    # Enable monitor mode on the wireless interface
    mon_iface = enable_monitor_mode(interface_name)

    if mon_iface is None:
        print("Error: Failed to enable monitor mode on interface " + interface_name)
        return

    # Capture wireless networks for the specified duration
    airodump_output_file = capture_wireless_networks(mon_iface, capture_duration)

    if airodump_output_file is None:
        print("Error: Failed to capture wireless networks")
        disable_monitor_mode(mon_iface)
        return

    # Parse the captured data into a list of network objects
    networks = parse_airodump_csv(airodump_output_file)

    # Save the networks and client information in a JSON file
    with open(output_file, "w") as json_file:
        json.dump(networks, json_file, indent=4, sort_keys=True)

    # Disable monitor mode on the wireless interface
    disable_monitor_mode(mon_iface)

    # Calculate and print metrics for the captured data
    metrics = get_metrics(networks)
    print_metrics(metrics, networks)

    # Return the networks and metrics for further processing
    return networks, metrics
