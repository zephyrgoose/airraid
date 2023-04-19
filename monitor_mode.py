#!/usr/bin/python3
# monitor_mode.py

import os
import subprocess


def disable_power_management(iface):
    print("Disabling power management...")
    os.system(f"sudo iw dev {iface} set power_save off")
    print("Power management disabled.")


def enable_power_management(iface):
    print("Enabling power management...")
    os.system(f"sudo iw dev {iface} set power_save on")
    print("Power management enabled.")


def enable_monitor_mode(iface):
    print("Attempting to enable monitor mode...")
    os.system(f"sudo airmon-ng start {iface} > /dev/null")
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
                enable_power_management(iface)
                return None
            else:
                mon_iface = iface
        else:
            mon_iface = iface
        print("Device in monitor mode.")
    if not mon_iface:
        print("Monitor mode is not enabled on any interface.")
        enable_power_management(iface)
        return None

    disable_power_management(mon_iface)
    return mon_iface


def disable_monitor_mode(mon_iface):
    print("Disabling monitor mode...")
    os.system(f"sudo airmon-ng stop {mon_iface} > /dev/null")
    print("Monitor mode disabled.")
    enable_power_management(mon_iface)
