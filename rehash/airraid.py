import os
import json
import time
import subprocess
import tempfile
import glob
import signal
import csv
from datetime import datetime
from monitor_mode import enable_monitor_mode, disable_monitor_mode
from interface_manager import get_wireless_interfaces, select_wireless_interface

def handle_interrupt_signal(signal_number, frame):
    print("\nReceived interrupt signal. Exiting...")
    if mon_iface:
        disable_monitor_mode(mon_iface)
    exit(0)

import subprocess
import tempfile

def capture_wireless_networks(mon_iface, capture_duration=15):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        output_file = temp_file.name
        cmd = f"timeout {capture_duration} airodump-ng -w {output_file} --output-format csv {mon_iface}"

        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during airodump-ng execution: {e}")
            return None

        # Find the generated CSV file
        csv_files = glob.glob(f"{output_file}*.csv")
        if csv_files:
            return csv_files[0]
        else:
            print("Error: Could not find the generated CSV file.")
            return None


def save_networks_csv(networks, filename="networks.csv"):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = networks[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in networks:
            writer.writerow(row)

def save_clients_csv(clients, filename="clients.csv"):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = clients[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in clients:
            writer.writerow(row)

def parse_airodump_csv(filename):
    networks = []
    clients = []

    with open(filename, "r") as file:
        content = file.read()
        sections = content.split("\n\n")

        if len(sections) >= 2:
            network_csv = csv.DictReader(sections[0].strip().split("\n"))
            client_csv = csv.DictReader(sections[1].strip().split("\n"))

            for row in network_csv:
                networks.append(row)
            for row in client_csv:
                clients.append(row)

    return networks, clients

mon_iface = None
def main():
    global mon_iface
    interfaces = get_wireless_interfaces()
    iface = select_wireless_interface(interfaces)

    if iface is not None:
        mon_iface = enable_monitor_mode(iface)

        if mon_iface is not None:
            airodump_output_file = capture_wireless_networks(mon_iface)
            if airodump_output_file is not None:
                networks = parse_airodump_csv(airodump_output_file)

                # Save the networks and client information in a JSON file
                with open("wireless_networks.json", "w") as json_file:
                    json.dump(networks, json_file, indent=4, sort_keys=True)

            disable_monitor_mode(mon_iface)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt_signal)
    main()
