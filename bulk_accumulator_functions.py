#!/usr/bin/python3
#bulk_accumulator_functions.py

import tempfile
import signal
import time
import csv
import os
import glob
import subprocess


def handle_interrupt_signal(signal_number, frame):
    print("\nReceived interrupt signal. Exiting...")
    if mon_iface:
        disable_monitor_mode(mon_iface)
    exit(0)

def get_capture_duration():
    default_duration = 15
    duration = input(f"Please enter capture duration in seconds (default is {default_duration} seconds): ")
    if duration == "":
        print(f"Capture duration is {default_duration} seconds.")
        return default_duration
    else:
        duration = int(duration)
        print(f"Capture duration is {duration} seconds.")
        return duration

def capture_wireless_networks(mon_iface, capture_duration):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        output_file = temp_file.name
        cmd = f"airodump-ng -w {output_file} --output-format csv -a {mon_iface} --berlin 20"

        try:
            process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
            time.sleep(capture_duration)
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait()
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
                # Remove leading spaces from keys
                row = {k.strip(): v.strip() for k, v in row.items()}
                # Remove LAN IP and Key fields
                row.pop("LAN IP", None)
                row.pop("Key", None)
                networks.append(row)

            for row in client_csv:
                # Remove leading spaces from keys
                row = {k.strip(): v.strip() for k, v in row.items()}
                clients.append(row)

    return {"networks": networks, "clients": clients}

def chance_of_cracking_10_minutes(network):
    return 0.1  # Replace with actual calculation

def chance_of_cracking_10_hours(network):
    return 0.5  # Replace with actual calculation

def chance_of_cracking_10_days(network):
    return 0.9  # Replace with actual calculation

def print_metrics(metrics, networks_data):
    print(f"Number of networks: {metrics['Number of networks']}")
    print(f"Number of clients: {metrics['Number of clients']}")
    print(f"{'SSID/BSSID':<35}{'Chance to crack in:':^31}")
    print(f"{'':<35}{'10 minutes':^22}{'10 hours':^22}{'10 days':^22}")

    for row in metrics["Table"]:
        ssid = get_ssid_by_bssid(row['Network'], networks_data)
        print(f"{ssid:<35}{row['Chance to crack in 10 minutes']:^22.2f}{row['Chance to crack in 10 hours']:^22.2f}{row['Chance to crack in 10 days']:^22.2f}")


def get_ssid_by_bssid(bssid, networks_data):
    for network in networks_data["networks"]:
        if network["BSSID"].strip() == bssid.strip():
            ssid = network["ESSID"].strip()
            return ssid if ssid else bssid
    return bssid


def get_metrics(json_data):
    networks = json_data["networks"]
    clients = json_data["clients"]

    networks_with_clients = [network for network in networks if any(client["BSSID"].strip() == network["BSSID"].strip() for client in clients)]

    table = []
    for network in networks_with_clients:
        row = {
            "Network": network["BSSID"].strip(),
            "Chance to crack in 10 minutes": chance_of_cracking_10_minutes(network),
            "Chance to crack in 10 hours": chance_of_cracking_10_hours(network),
            "Chance to crack in 10 days": chance_of_cracking_10_days(network),
        }
        table.append(row)

    metrics = {
        "Number of networks": len(networks),
        "Number of clients": len(clients),
        "Table": table,
    }

    return metrics
