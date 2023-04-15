import subprocess
import time
import re

def parse_airodump_output(output):
    networks = []
    pattern = re.compile(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})')

    lines = output.split('\n')
    for index, line in enumerate(lines):
        if pattern.search(line):
            bssid = pattern.search(line).group()
            row = line.split()

            channel = row[2]
            encryption = row[4]
            essid = lines[index + 1].strip()
            
            networks.append({
                'bssid': bssid,
                'channel': channel,
                'essid': essid,
                'encryption': encryption
            })

    return networks

def scan_wifi_networks(interface, scan_duration=10):
    airodump_process = subprocess.Popen(['airodump-ng', interface],
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    
    time.sleep(scan_duration)
    airodump_process.terminate()
    
    output, _ = airodump_process.communicate()
    
    networks = parse_airodump_output(output)
    
    return networks

if __name__ == "__main__":
    # Replace 'wlan0mon' with your wireless interface in monitor mode
    interface = 'wlan0mon'
    
    networks = scan_wifi_networks(interface)
    for network in networks:
        print(network)
 
