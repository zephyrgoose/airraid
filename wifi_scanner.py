import os
import sys
import signal
import subprocess
import time
import threading
from datetime import datetime
from scapy.all import *
from collections import defaultdict

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def process_packet(packet):
    if packet.haslayer(Dot11Beacon):
        bssid = packet[Dot11].addr2
        ssid = packet[Dot11Elt].info.decode()
        channel = int(packet[Dot11Elt:3].info[0])
        signal_strength = packet.dBm_AntSignal

        if bssid not in networks:
            networks[bssid] = (ssid, channel, signal_strength)
            print(f"SSID: {ssid}, BSSID: {bssid}, Channel: {channel}, Signal: {signal_strength} dBm")
        else:
            ssid, channel, signal_strength = networks[bssid]
            networks[bssid] = (ssid, channel, max(signal_strength, packet.dBm_AntSignal))

        # Retrieve the top 3 most active clients for the BSSID
        clients = get_top_clients(bssid, 3)
        client_str = ','.join(clients) if clients else 'None'
        print(f"    Top clients: {client_str}")


def select_networks():
    if not networks:
        print("No networks found. Exiting.")
        sys.exit(0)

    sorted_networks = sorted(networks.items(), key=lambda x: x[1][2], reverse=True)

    for i, (bssid, (ssid, channel, signal)) in enumerate(sorted_networks, start=1):
        print(f"{i}. SSID: {ssid}, BSSID: {bssid}, Channel: {channel}, Signal: {signal} dBm")

    selected_indices = input("Select networks to target (comma-separated numbers): ").split(',')
    selected_bssids = [sorted_networks[int(index) - 1][0] for index in selected_indices]
    return selected_bssids



def choose_action(selected_bssids):
    action_options = [
        "Crack the password now",
        "Save network information as a hashcat-friendly text file"
    ]
    print("\nAvailable actions:")
    for i, option in enumerate(action_options, 1):
        print(f"{i}. {option}")

    action = int(input("Choose an action (enter the number): "))
    return action

def countdown_timer(timeout):
    global interrupted
    for remaining in range(timeout, 0, -1):
        if interrupted:
            break
        sys.stdout.write(f"\rTime remaining: {remaining:2d} seconds")
        sys.stdout.flush()
        time.sleep(1)

def get_top_clients(bssid,amount):
    clients = defaultdict(int)
    def count_client(pkt):
        if pkt.haslayer(Dot11) and pkt.addr2 == bssid:
            clients[pkt.addr1] += 1

    # Sniff packets for 5 seconds to capture clients
    sniff(iface=mon_iface, prn=count_client, timeout=5)

    # Get the top 3 clients with the highest number of packets
    top_clients = sorted(clients.items(), key=lambda x: x[1], reverse=True)[:amount]

    # Return the MAC addresses of the top 3 clients
    return [client[0] for client in top_clients]


interrupted = False
if __name__ == "__main__":
    networks = {}
    signal.signal(signal.SIGINT, signal_handler)

    print("Scanning for Wi-Fi interfaces...")
    interfaces = os.popen("iwconfig 2>/dev/null | grep '^[a-zA-Z]' | awk '{print $1}'").read().splitlines()

    wifi_interfaces = [iface for iface in interfaces if "wlan" in iface or "wlp" in iface]

    if not wifi_interfaces:
        print("No Wi-Fi interfaces found.")
        sys.exit(1)

    if len(wifi_interfaces) == 1:
        iface = wifi_interfaces[0]
        print(f"Using Wi-Fi interface: {iface}")
    else:
        for i, iface in enumerate(wifi_interfaces, 1):
            print(f"{i}. {iface}")
        iface_index = int(input("Select an interface to use (enter the number): ")) - 1
        iface = wifi_interfaces[iface_index]

    print("Enabling monitor mode...")
    os.system(f"sudo airmon-ng start {iface}")
    mon_iface = os.popen("iwconfig 2>/dev/null | grep '^[a-zA-Z]' | grep 'Mode:Monitor' | awk '{print $1}'").read().strip()

    if not mon_iface:
        print(f"Checking monitor mode status for interface {iface}...")
        iwconfig_output = subprocess.check_output(["iwconfig", iface])
        if b"Mode:Monitor" not in iwconfig_output:
            os.system(f"sudo ifconfig {iface} down")
            os.system(f"sudo iwconfig {iface} mode monitor")
            os.system(f"sudo ifconfig {iface} up")

            iwconfig_output = subprocess.check_output(["iwconfig", iface])
            if b"Mode:Monitor" not in iwconfig_output:
                print("Failed to enable monitor mode.")
                sys.exit(1)
            else:
                mon_iface = iface
        else:
            mon_iface = iface
    if not mon_iface:
        print("Monitor mode is not enabled on any interface. Exiting.")
        sys.exit(1)

    # Add these lines to prompt for timeout duration
    timeout_duration = int(input("Enter the desired timeout duration for Wi-Fi scan (in seconds, default is 30): ") or 30)

    # Add these lines to start the countdown timer thread
    timeout_thread = threading.Thread(target=countdown_timer, args=(timeout_duration,))
    timeout_thread.start()

    print(f"Monitor mode enabled on {mon_iface}. Starting Wi-Fi scan...")

    # Add 'timeout=timeout_duration' parameter to the sniff function and handle KeyboardInterrupt
    try:
        start_time = time.time()
        while time.time() - start_time < timeout_duration:
            try:
                sniff(iface=mon_iface, prn=process_packet, timeout=1)
                remaining_time = timeout_duration - (time.time() - start_time)
                sys.stdout.write(f"\rTime remaining: {int(remaining_time)} seconds")
                sys.stdout.flush()
            except KeyboardInterrupt:
                interrupted = True
                break
        sys.stdout.write("\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        interrupted = True


    # Present available networks and choose action
    selected_bssids = select_networks()
    action = choose_action(selected_bssids)

    if action == 1:
        # Crack the password now
        pass
    elif action == 2:
        # Save network information as a hashcat-friendly CSV file
        filename = "wifi_networks.csv"
        with open(filename, 'a') as f:
            for bssid in selected_bssids:
                ssid, channel, signal_strength = networks[bssid]

                clients = get_top_clients(bssid,3)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                f.write(f"{ssid},{bssid},{channel},{','.join(clients)},{current_time}\n")

        print(f"Network information saved to {filename}.")
    else:
        print("Invalid action. Exiting.")

    print("Disabling monitor mode...")
    os.system(f"sudo airmon-ng stop {mon_iface}")
    print("Operation complete.")
