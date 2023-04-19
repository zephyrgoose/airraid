#!/usr/bin/python3
# bulk_accumulator.py

import json
import signal
from monitor_mode import enable_monitor_mode, disable_monitor_mode
from interface_manager import get_wireless_interfaces, select_wireless_interface
from bulk_accumulator_functions import get_capture_duration, capture_wireless_networks, parse_airodump_csv, handle_interrupt_signal, get_metrics, print_metrics

mon_iface = None


def main():

    global mon_iface
    interfaces = get_wireless_interfaces()
    iface = select_wireless_interface(interfaces)

    if iface is not None:
        mon_iface = enable_monitor_mode(iface)

        if mon_iface is not None:
            capture_duration = get_capture_duration()
            airodump_output_file = capture_wireless_networks(mon_iface, capture_duration)
            if airodump_output_file is not None:
                networks = parse_airodump_csv(airodump_output_file)

                # Save the networks and client information in a JSON file
                with open("wireless_bulk.json", "w") as json_file:
                    json.dump(networks, json_file, indent=4, sort_keys=True)

            disable_monitor_mode(mon_iface)
            metrics = get_metrics(networks)
            print_metrics(metrics, networks)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt_signal)
    main()
