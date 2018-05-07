#! /usr/bin/env python
"""
Simple script to allow a user to obtain the list of all Sensors (Software and Hardware)
from the Tetration Platform

Requires the Tetration API Client: pip install tetpyclient

TO DO:
* Currently returns a host entry per Interface. So if a host has 6 interfaces, will return the same host 6 times
    1 for each interface, even though the details are identical. Need to summarize interfaces, and print host
    only once and then all the associated interfaces, to clean it up and make it more presentable

Reference:
https://github.com/tetration-exchange/devnet-2423/

Michael Petrinovic 2018
"""

import traceback
from tetpyclient import RestClient
import requests.packages.urllib3
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tabulate import tabulate
from datetime import datetime

def get_sensors(session):
    """
    Tetration API call for Software Sensors
    """
    sensors = {}

    #print all_sensors
    print str(len(sensors))

    resp = session.get('/openapi/v1/sensors')
    sensor_list = []

    sensors = resp.json()

    for entry in sensors['results']:
        for item in entry['interfaces']:
            if item.get('vrf', None) == 'Tetration':
                continue
            else:
                intf = list(map(lambda x: {"ip": x['ip'], "type": x['family_type'],
                                           "vrf": x['vrf'], "mac": x['mac']}, entry['interfaces']))
                print "=" * 80
                print entry['host_name']
                for my_int in intf:
                    print "-" * 40
                    print my_int['ip']
                    print my_int['mac']
                    print my_int['type']
                    print my_int['vrf']
                print "=" * 80
                sensor_list.append((entry['uuid'], entry['cpu_quota_usec'],
                                    entry['platform'], entry['host_name'],
                                    entry['current_sw_version'],entry['enable_pid_lookup'],entry['agent_type']))
    return sensor_list

def get_hw_sensors(session):
    #here
    resp = session.get('/openapi/v1/switches')
    hw_sensor_list = []

    if resp.status_code == 200:
        hw_sensors = resp.json()

        for entry in hw_sensors:
            hw_sensor_list.append((entry['name'], entry['ip'],
                                   datetime.fromtimestamp(entry["last_checkin_epoch"]),
                                   entry['nxos_version'],
                                   entry['role'],entry['agent_version']))
    else:
        # Response code != 200, meaning issue occurred or zero sensors found
        print "Unsuccessful request returned code: {} , response: {}".format(resp.status_code,resp.text)
        return

    return hw_sensor_list

def get_parser():
    '''
    Get parser object for script
    '''
    #from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            add_help=True,
                            version="1.0")
    parser.add_argument("-c", "--credentials", required=True, help="Specify the credentials file to use")
    parser.add_argument("-p", "--platform", required=True, help="The IP or DNS name for your Tetration platform. Eg: https://<VIP/DNS>.cisco.com")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", default=False, help="Enable debug output")
    return parser


def main():
    """
    Main routine to be executed
    """
    # Get the CLI arguements
    args = get_parser().parse_args()

    if args.debug:
        print ("\n\n")
        print ("Credentials file: " + args.credentials)
        print ("Tetration Platform: " + args.platform)
        print ("\n\n")
    API_ENDPOINT = args.platform
    API_CREDENTIALS = args.credentials

    RC_SESSION = RestClient(API_ENDPOINT, credentials_file=API_CREDENTIALS, verify=False)
    requests.packages.urllib3.disable_warnings()

    try:
        sensors = get_sensors(RC_SESSION)
        # Print out all the data collected
        print ("\n")
        print ("Software Sensors")
        print (tabulate(sensors, headers = ["UUID", "CPU Quota", "Platform", "Hostname",
                                            "Current SW Ver", "PID Lookup",
                                            "Agent Type"], tablefmt="orgtbl"))

        my_hardware = get_hw_sensors(RC_SESSION)
        # Print out all the data collected
        print ("\n")
        print ("Hardware Sensors")
        print (tabulate(my_hardware, headers = ["Name", "IP", "Last Check-in", "NX-OS Version",
                                            "Role", "Agent Version"], tablefmt="orgtbl"))

        sw_summary = "Total Software Sensors: " + str(len(sensors))
        print "=" * len(sw_summary)
        print sw_summary
        print "=" * len(sw_summary)

        hw_summary = "Total Hardware Sensors: " + str(len(my_hardware))
        print "=" * len(hw_summary)
        print hw_summary
        print "=" * len(hw_summary)


    except Exception, err:
        print "Operation failed"
        print traceback.format_exc(err)


if __name__ == '__main__':
    main()
