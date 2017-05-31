# zigbee_server.py
Web server to manage zigbee shades
This program is provided "as is" and has been developped to work with Telegesis Zigbee USB Dongle (ETRX357 USB) connected to a Raspberry Pi.
It has been coded to work with Domoticz but can be easily adapted to work with other system: the program act itself as a web server listening for command on port 1234

# Error code from https://www.silabs.com
00 Everything OK - Success
01 Couldn’t poll Parent because of Timeout
02 Unknown command
04 Invalid S-Register
05 Invalid parameter
06 Recipient could not be reached
07 Message was not acknowledged
08 No sink known
09 Address Table entry is in use and cannot be modified
0A Message could not be sent
0B Local node is not sink
0C Too many characters
0E Background Scan in Progress (Please wait and try again)
0F Fatal error initialising the network
10 Error bootloading
12 Fatal error initialising the stack
18 Node has run out of Buffers
19 Trying to write read-only register
1A Data Mode Refused by Remote Node
1B Connection Lost in Data Mode
1C Remote node is already in Data Mode
20 Invalid password
25 Cannot form network
27 No network found
28 Operation cannot be completed if node is part of a PAN
2C Error leaving the PAN
2D Error scanning for PANs
33 No response from the remote bootloader
34 Target did not respond during cloning
35 Timeout occurred during xCASTB
39 MAC Transmit Queue is Full
6C Invalid Binding Index
70 Invalid Operation
72 More than 10 unicast messages were in flight at the same time
74 Message too long
80 ZDP Invalid Request Type
81 ZDP Device not Found
82 ZDP Invalid Endpoint
83 ZDP Not Active
84 ZDP Not Supported
85 ZDP Timeout
86 ZDP No Match
87 ZDP Table Full
88 ZDP No Entry
89 ZDP No Descriptor
91 Operation only possible if connected to a PAN
93 Node is not part of a Network
94 Cannot join network
96 Mobile End Device Move to new Parent Failed
98 Cannot join ZigBee 2006 Network as Router
A1 More than 8 broadcasts were sent within 8 seconds
AB Trying to join, but no beacons could be heard
AC Network key was sent in the clear when trying to join secured
AD Did not receive Network Key
AE No Link Key received
AF Preconfigured Key Required
C5 NWK Already Present
C7 NWK Table Full
C8 NWK Unknown Device
