import json

def process_wireless_data(wireless_data):
    networks = wireless_data["networks"]
    clients = wireless_data["clients"]
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

def main():
    with open("wireless_bulk.json", "r") as file:
        data = json.load(file)

    return process_wireless_data(data)

if __name__ == "__main__":
    results = main()
    print(results)
