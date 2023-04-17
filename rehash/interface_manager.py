import os
import subprocess

def get_wireless_interfaces():
    iwconfig_output = os.popen("iwconfig 2>/dev/null | grep '^[a-zA-Z]' | grep -v 'no wireless extensions' | awk '{print $1}'").read()
    interfaces = iwconfig_output.split("\n")[:-1]
    return interfaces

def select_wireless_interface(interfaces):
    if not interfaces:
        print("No wireless interfaces found.")
        return None

    if len(interfaces) == 1:
        return interfaces[0]

    print("Select a wireless interface:")
    for idx, iface in enumerate(interfaces):
        print(f"{idx + 1}. {iface}")

    while True:
        try:
            selection = int(input("Enter the number of the interface you want to use: ")) - 1
            if 0 <= selection < len(interfaces):
                return interfaces[selection]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
