#!/usr/bin/python3
# handshake_capturer.py

import os
import subprocess
import time

def capture_handshake(interface_name, station_mac, station_essid, station_channel, timeout):
    output_prefix = "network-traffic"
    start_time = time.time()

    airodump_process = subprocess.Popen([
        "sudo", "airodump-ng", "-w", output_prefix, "--bssid", station_mac, "--channel", str(station_channel),
        "--output-format", "pcap", "--write-interval", "2", interface_name
    ])

    try:
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print("Timeout reached.")
                break

            # Check for the existence of a 4-way handshake
            hcxpcapngtool_process = subprocess.run(
                ["hcxpcapngtool", "-o", "hash", f"{output_prefix}-01.cap"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            if os.path.exists("hash"):
                print("Handshake captured.")
                break

            # Wait for a short period before checking again
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C). Shutting down gracefully.")
    finally:
        airodump_process.terminate()
        airodump_process.wait()

        # Clean up the files
        cap_file = f"{output_prefix}-01.cap"
        if os.path.exists("hash"):
            os.makedirs("captured_hashes", exist_ok=True)
            os.rename("hash", f"captured_hashes/{station_essid}-captured-hash")
        if os.path.exists(cap_file):
            os.remove(cap_file)



interface_name = "wlp0s20f0u4"  # Monitor mode interface name
station_mac = "72:CD:D6:A1:EB:A6"  # Station MAC address
station_channel = 3  # Station channel
timeout = 6000  # Timeout in seconds

capture_handshake(interface_name, station_mac, "test-essid", station_channel, timeout)
