#!/usr/bin/python3
# bulk_discriminator.py

import json

def process_wireless_data():
    with open("wireless_bulk.json", "r") as file:
        data = json.load(file)
        networks = data["networks"]
        clients = data["clients"]
        results = []

        for network in networks:
            associated_clients = [client for client in clients if client["BSSID"] == network["BSSID"]]
            if associated_clients:
                result = {
                    'ESSID': network['ESSID'],
                    'number_of_clients': len(associated_clients),
                    'station_mac': network['BSSID'],
                    'client_mac_addresses': [client["Station MAC"] for client in associated_clients]
                }
                results.append(result)
        return results

results = process_wireless_data()
print(results)
