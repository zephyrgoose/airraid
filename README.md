# airraid
This is a BIG work-in-progress

Airraid glues together aircrack-ng, hashcat, and some forethought. Airraid is autonomous, and uses OSINT to try to accelerate the password cracking phase. You can also collect hashes to try in hashcat later.

Currently, it just collates network and client information in a big json file called wireless_bulk.json.

Run bulk_accumulator.py with python using sudo

Tested and created with python 3.10.10.

Required Linux packages [version tested on]:
- aircrack-ng [1.7]
- iwconfig [WT-30]
- net-tools [2.10]
- hashcat [6.2.6]

Required python packages (currently all built-in):
- tempfile
- signal
- time
- csv
- os
- glob
- subprocess
