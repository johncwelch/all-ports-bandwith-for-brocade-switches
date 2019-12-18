# all-ports-bandwith-for-brocade-switches
Python script that acts as a nagios probe for getting bandwidth measurements for all ports on a brocade switch

This version is the initial attempt. Currently it only handles SNMP v2 but the start of v3 support is in there. As this uses the brocade private MIB (technically Foundry) to get the Kbps in/out of each port, it's only going to work with Brocade gear. 
