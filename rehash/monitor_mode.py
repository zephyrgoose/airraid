import os
import subprocess

def enable_monitor_mode(iface):
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
                return None
            else:
                mon_iface = iface
        else:
            mon_iface = iface

    if not mon_iface:
        print("Monitor mode is not enabled on any interface.")
        return None

    return mon_iface

def disable_monitor_mode(mon_iface):
    print("Disabling monitor mode...")
    os.system(f"sudo airmon-ng stop {mon_iface}")
    print("Monitor mode disabled.")
