Sample script that allows you to extract all of the sensors (both Hardware and Software) connected to the Tetration Platform, and provide you with information about each sensor. 

It will produce output that collects the following information:
* Software Sensors:
** UUID
** CPU Quota
** Platform
** Hostname
** Current S/W Version
** PID Lookup
** Agent Type (Deep Visibility Agent / Universal Visibility Agent / Enforcement Agent)

* Hardware Sensors:
** Name
** IP
** Last Check-In
** NX-OS Version
** Role
** Agent Version

* Furthermore, the script will also provide you with a breakdown of each host (that has a Software agent installed), what interfaces they have configured, and other information such as IP and MAC Address


> Reminder: The -c specifies your credentials .json file that you should have downloaded from your Tetration Platform when enabling the API keys

Get Sensors
```YAML
# python tetration_sensors_sw_hw.py -c kangaroo_sa_credentials.json -p https://kangaroo.cisco.com
```

Created by Michael Petrinovic 2018


WARNING:

These scripts are meant for educational/proof of concept purposes only - as demonstrated at Cisco Live and/or my other presentations. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and I am not responsible for any damage or data loss incurred as a result of their use
