# airraid
This is a BIG work-in-progress

Airraid glues together aircrack-ng, hashcat, and some forethought. It uses
simple OSINT hints (based on the target's OUI) to estimate password strength and
speed up cracking. Handshakes can also be collected for later use with hashcat.


Usage revolves around a single entry point:

```
sudo python3 airraid.py
```

The program scans nearby networks, analyses them and lists those with connected
clients. Select a target and airraid will attempt to capture a WPA handshake
automatically. Captured hashes are saved to `captured_handshakes/`.

The helper scripts remain for reference but are not required for everyday usage.



Tested and created with python 3.10.10.
Required Linux packages [version tested on]:
- asyncio	[3.4.3]
- aircrack-ng	[1.7]	(built-in)
- iwconfig	[WT-30]	(built-in)
- net-tools	[2.10]	(built-in)
- hashcat	[6.2.6]	(built-in)
To run the unit tests:

```
pytest -q
```

If the `pytest-cov` plugin is installed you can obtain coverage with:

```
pytest --cov=.
```


Required python packages (currently all built-in):
- tempfile
- signal
- time
- csv
- os
- glob
- subprocess
