import argparse
import os
import sys
from scapy.all import *

def handshake_filter(pkt, client_mac, wap_mac):
    # Check if packet is a 4-way handshake
    if pkt.haslayer(EAPOL) and pkt[EAPOL].type == 3:
        # Check if packet is between specified client and WAP MAC addresses
        if pkt.addr1 == client_mac and pkt.addr2 == wap_mac:
            return True
    return False

def capture_handshake(mon_iface, client_mac, wap_mac):
    # Start capturing packets on the specified interface
    print(f"Capturing 4-way handshake on {mon_iface}...")
    sniff(iface=mon_iface, prn=lambda pkt: handle_packet(pkt, client_mac, wap_mac), filter="ether proto 0x888e")

def handle_packet(pkt, client_mac, wap_mac):
    # Check if packet matches filter criteria
    if handshake_filter(pkt, client_mac, wap_mac):
        # Save captured packets to file
        timestamp = int(time.time())
        filename = f"handshake_{timestamp}.pcap"
        wrpcap(filename, pkt, append=True)
        print(f"4-way handshake captured and saved to {filename}")
        # Stop capturing packets and exit program
        sys.exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Capture WPA2-PSK 4-way handshake")
    parser.add_argument("interface", help="Wi-Fi interface name in monitor mode")
    parser.add_argument("client_mac", help="MAC address of the client device")
    parser.add_argument("wap_mac", help="MAC address of the WAP")
    args = parser.parse_args()

    # Start capturing packets and wait for handshake to be captured
    capture_handshake(args.interface, args.client_mac, args.wap_mac)
