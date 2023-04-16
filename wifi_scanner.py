import os
import sys
import signal
import subprocess
import time
import threading
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

        if bssid not in networks:
            networks[bssid] = (ssid, channel)
            print(f"SSID: {ssid}, BSSID: {bssid}, Channel: {channel}")

def select_networks():
    print("\nAvailable networks:")
    for i, (bssid, (ssid, channel)) in enumerate(networks.items(), 1):
        print(f"{i}. SSID: {ssid}, BSSID: {bssid}, Channel: {channel}")

    selected_indices = input("Select networks to target (comma-separated numbers): ").split(',')
    selected_bssids = [list(networks.keys())[int(index) - 1] for index in selected_indices]

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


    print(f"Monitor mode enabled on {mon_iface}. Starting Wi-Fi scan...")

    # Add these lines to start the countdown timer thread
    timeout_thread = threading.Thread(target=countdown_timer, args=(timeout_duration,))
    timeout_thread.start()

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
        print("CRACKING DA PASSWORD NOW")
        pass
    elif action == 2:
        # Save network information as a hashcat-friendly text file
        filename = "wifi_networks.txt"
        with open(filename, 'w') as f:
            for bssid in selected_bssids:
                ssid, channel = networks[bssid]
                f.write(f"{ssid},{bssid},{channel}\n")

        print(f"Network information saved to {filename}.")
    else:
        print("Invalid action. Exiting.")

    print("Disabling monitor mode...")
    os.system(f"sudo airmon-ng stop {mon_iface}")
    print("Operation complete.")
