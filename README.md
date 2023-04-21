# airraid
This is a BIG work-in-progress

Airraid glues together aircrack-ng, hashcat, and some forethought. Airraid is autonomous, and uses OSINT to try to accelerate the password cracking phase. You can also collect hashes to try in hashcat later.


Since this is a WIP, there are several seperate scripts mean to be ran by the end-user:
- airraid.py
- bulk_discriminator.py
- handshake_capturer.py

I'm fairly sure all of them need sudo.

airraid.py currently runs bulk_accumulator.py, which works to create wireless_bulk.json, a file collecting details about wireless networks and clients.

bulk_discriminator.py performs analysis on wireless_bulk.json, and is meant to be ran after (at least after starting) bulk_accumulator.py.

handshake_capturer.py takes various network and client details as inputs, and listens for 4-way handshakes. If it detects one it automatically saves the handshake to captured_handshakes/, deleteds the temporary files used, and exits gracefully.



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
