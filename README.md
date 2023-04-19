# airraid
This is a BIG work-in-progress

Airraid glues together aircrack-ng, hashcat, and some forethought. Airraid is autonomous, and uses OSINT to try to accelerate the password cracking phase. You can also collect hashes to try in hashcat later.

Currently, it just collates network and client information in a big json file called wireless_bulk.json.

Run bulk_accumulator.py with python using sudo

Tested and created with python 3.10.10.

Required Linux packages [version tested on]:
- pyrcrack	[1.2.6]
- asyncio	[3.4.3]
- aircrack-ng	[1.7]	(built-in)
- iwconfig	[WT-30]	(built-in)
- net-tools	[2.10]	(built-in)
- hashcat	[6.2.6]	(built-in)

Required python packages (currently all built-in):
- tempfile
- signal
- time
- csv
- os
- glob
- subprocess
