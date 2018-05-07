#! /usr/bin/env python
"""
Simple script to allow a user to obtain the list of flows,
in addition to the TopN destination providers, then link that to the TopN source address
for each individual of the TopN destination providers

Requires the Tetration API Client: pip install tetpyclient

TO DO:
* All testing has been for a DNS use case. Need to test various other common ports
* At present, the filter from the CLI (--provider) is only applicable to the FlowSearch output.
    - It does NOT apply to the TopN query that takes place later in the execution

Reference:
https://github.com/tetration-exchange/devnet-2423/

Michael Petrinovic 2018
"""
import json
import requests.packages.urllib3
from tetpyclient import RestClient
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tabulate import tabulate
from datetime import datetime
from datetime import timedelta


CURRENT_POST_ENDPOINT = '/flowsearch'
CURRENT_POST_TOPN_ENDPOINT = '/flowsearch/topn'

def topN_query(t0, t1, dst_ip, dst_port):
    SUBSEQUENT_POST_TOPN_PAYLOD = {
        "t0": t0.strftime('%s'),
        "t1": t1.strftime('%s'),
        "dimension": "src_address",
        "metric": "fwd_pkts",
        "filter": {"type": "and",
            "filters": [
                {"type": "eq", "field": "dst_address", "value": dst_ip},
                {"type": "eq", "field": "dst_port", "value": dst_port}
            ]
        },
        "threshold": 10, # the N in the topN
        "scopeName": "Default"
    }
    return SUBSEQUENT_POST_TOPN_PAYLOD

def my_nslookup(ip):
    #import re
    import dns.reversename
    import dns.resolver
    # myResolver = dns.resolver.Resolver()
    # myResolver.nameservers = ['64.104.200.248']
    try:
        domain_address = dns.reversename.from_address(ip)
        #print domain_address
        #print dns.reversename.to_address(domain_address)
        domain_name = str(dns.resolver.query(domain_address,"PTR")[0])
        return domain_name
    except:
        return "No DNS entry"

def get_parser():
    '''
    Get parser object for script
    '''
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            add_help=True,
                            version="1.0")
    parser.add_argument("-c", "--credentials", required=True, help="Specify the credentials file to use")
    parser.add_argument("-p", "--platform", required=True, help="The IP or DNS name for your Tetration platform. Eg: https://<VIP/DNS>.cisco.com")
    parser.add_argument("--port", help="The port number you want to search for", default="80")
    parser.add_argument("--provider", help="The IP of the authorized/trusted server providing the service. Eg: DNS, HTTP, AD servers")
    parser.add_argument("--hours", choices=xrange(1, 25), default=1, type=int, help="How many hours to search. 1-24")
    parser.add_argument("--filter", choices=["eq", "ne"], default="ne", help="How to search with Provider. Flows equal to that Provider (eq) or not with that Provider (ne)")
    parser.add_argument("--limit", default=100, type=int, help="Limit the number of results within the last 24 hours to this value (1-1000)")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", default=False, help="Enable debug output")
    return parser


def main():
    # Get the CLI arguements
    args = get_parser().parse_args()

    if args.debug:
        print ("\n")
        print ("Credentials file: " + args.credentials)
        print ("Tetration Platform: " + args.platform)
        print ("\n")
    API_ENDPOINT = args.platform
    API_CREDENTIALS = args.credentials

    # The HTTP Body should be sent in JSON format. The Python Client will set the Content-Type as
    # application/json

    now = datetime.now()
    t1 = now # - timedelta(minutes=360)
    t0 = t1 - timedelta(hours=args.hours)

    dst_port = args.port
    dst_ip = args.provider

    # Used to find all flows for the time window specified. Max is 24 hours, with 1000 records
    CURRENT_POST_PAYLOAD = {
      "t0": t0.strftime('%s'),
      "t1": t1.strftime('%s'),
      "limit": args.limit,
      "filter": {
        "type": "and",
        "filters": []
        }
    }

    if dst_ip is not None:
        CURRENT_POST_PAYLOAD['filter']['filters'].append({
            "type": args.filter,
            "field": "dst_address",
            "value": dst_ip ##dst_ip
        })

    if dst_port is not None:
        CURRENT_POST_PAYLOAD['filter']['filters'].append({
            "type": "eq",
            "field": "dst_port",
            "value": dst_port
        })

    # Used to find the TopN Providers for the specified port
    CURRENT_POST_TOPN_PAYLOAD = {
        "t0": t0.strftime('%s'),
        "t1": t1.strftime('%s'),
        "dimension": "dst_address",
        "metric": "fwd_pkts",
        "filter": {"type": "eq", "field": "dst_port", "value": args.port},
        "threshold": 10, # the N in the topN
        "scopeName": "Default"
    }

    if args.debug:
        print ("Flow Search Payload to POST: ")
        print json.dumps(CURRENT_POST_PAYLOAD, indent = 4)
        print ("\n\n")

    if args.debug:
        print ("Flow TopN Search Payload to POST: ")
        print json.dumps(CURRENT_POST_TOPN_PAYLOAD, indent = 4)
        print ("\n\n")

    # Create a new RestClient connection for API communication
    rc = RestClient(API_ENDPOINT, credentials_file=API_CREDENTIALS, verify=False)
    # Disable warnings
    requests.packages.urllib3.disable_warnings()

    # Post the CURRENT_POST_PAYLOAD to the API ENDPOINT
    resp = rc.post(CURRENT_POST_ENDPOINT,json_body=json.dumps(CURRENT_POST_PAYLOAD))

    # Check for valid response
    if resp.status_code == 200:
        results = resp.json()
        #print results
    else:
        print "Unsuccessful request returned code: {} , response: {}".format(resp.status_code,resp.text)
        return

    flow_list = []

    # Loop through the results, finding the specific flows returned
    for entry in results["results"]:
        flow_list.append((entry['src_hostname'], entry['src_address'],
                            entry['src_port'], entry['dst_port'],
                            entry['dst_address'],entry['dst_hostname'], entry['proto'],
                            entry['fwd_pkts'], entry['rev_pkts'], entry['vrf_name']))

    # Make use of tabulate, to assist with auto-formating a table for print with the collected data
    print (tabulate(flow_list, headers = ["Src Hostname", "Src Address", "Src Port",
                                          "Dst Port", "Dst Address", "Dst Hostname",
                                          "Protocol", "Fwd Pkts", "Rev Pkts", "VRF"], tablefmt="orgtbl"))
    print "\n"
    summary = "Total Flows: " + str(len(flow_list)) # Should match the CLI --limit or 1000 (as the max inbuilt value)
    print "=" * len(summary)
    print summary
    print "=" * len(summary) + "\n"

    # Do similar to above, flowsearch, this time identifying the Top N hosts in the communication
    topN_list = []
    prov_count = 1

    # New Remote Connection to query the TopN API, using the CURRENT_POST_TOPN_PAYLOAD
    resp = rc.post(CURRENT_POST_TOPN_ENDPOINT,json_body=json.dumps(CURRENT_POST_TOPN_PAYLOAD))

    # Check for valid response (200 - ok)
    if resp.status_code == 200:
        results = resp.json()

        # Loop through the results returned
        for entry in results[0]['result']:
            # Perform a DNS lookup, using the local system's DNS providers - i.e. the host running this script
            dns_name = my_nslookup(entry['dst_address'])

            # For each entry, append to the list
            # #1, IP Address, DNS lookup, "" = empty for Source Address, Packet Count
            topN_list.append((prov_count, entry['dst_address'], dns_name, "", "Total: " + str(entry['fwd_pkts'])))

            # Perform a second query, this time matching all flows for
            # the port number specified AND the current provider 'dst_address'
            # Do this by calling my function, to return the JSON paylod required
            subsequent_query = topN_query(t0, t1, entry['dst_address'], args.port)
            sub_resp = rc.post(CURRENT_POST_TOPN_ENDPOINT,json_body=json.dumps(subsequent_query))

            # Again, check for valid response
            if sub_resp.status_code == 200:
                cons_results = sub_resp.json()
                provider_seen_before = False
                for cons_entry in cons_results[0]['result']:
                    if not provider_seen_before:
                        # print entry = Provider IP Address, Source IP Address, Packet Count
                        topN_list.append(("", "", "", cons_entry['src_address'], cons_entry['fwd_pkts']))
                        provider_seen_before = True
                    else:
                        # print entry = Provider empty as in the top line of this section, Source IP Address, Packet Count
                        topN_list.append(("", "", "", cons_entry['src_address'], cons_entry['fwd_pkts']))
            prov_count += 1
            # Add a blank line between each Destination Provider for clarity - since all in the same topN_list
            separator = "-" * 15
            topN_list.append((separator, separator, separator, separator, separator))
    else:
        print "Unsuccessful request returned code: {} , response: {}".format(resp.status_code,resp.text)
        return

    # Print out the summary tables for the TopN Destination Providers and consuming Source Addresses per Provider
    print ("TopN Table : Summary for Source Addresses consuming the Destination Provider on Port: %s") % (str(args.port) + "\n")
    print (tabulate(topN_list, headers = ["#", "Top N\nProvider", "DNS Lookup", "TopN\nSource Address\nPer Provider", "Packets"],
                    tablefmt="orgtbl", numalign="center", stralign="center"))
    print "\n"

if __name__ == '__main__':
    main()
