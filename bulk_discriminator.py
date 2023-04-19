#!/usr/bin/python3
# bulk_discriminator.py

import json


def process_wireless_data(wireless_data):
    networks = wireless_data["networks"]
    clients = wireless_data["clients"]
    result = []

    # Create a dictionary to map BSSID to ESSID
    bssid_to_essid = {network["BSSID"]: network["ESSID"] for network in networks}

    # Group clients by their associated Station MAC
    associated_clients = {}
    for client in clients:
        station_mac = client["Station MAC"]
        if station_mac not in associated_clients:
            associated_clients[station_mac] = []
        associated_clients[station_mac].append(client["BSSID"])

    for station_mac, client_macs in associated_clients.items():
        # Ignore networks without associated clients
        if station_mac == "(not associated)":
            continue

        essid = bssid_to_essid.get(station_mac, station_mac)

        network_data = {
            "ESSID": essid,
            "number_of_clients": len(client_macs),
            "station_mac": station_mac,
            "client_mac_addresses": client_macs
        }

        result.append(network_data)

    return result


def main():
    try:
        with open("wireless_bulk.json", "r") as f:
            wireless_bulk_data = json.load(f)
    except FileNotFoundError:
        print("Error: 'wireless_bulk.json' not found in the current directory.")
        exit()

    processed_data = process_wireless_data(wireless_bulk_data)
    print(processed_data)


if __name__ == "__main__":
    main()
