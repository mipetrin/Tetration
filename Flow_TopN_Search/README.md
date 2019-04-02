Simple script to allow a user to obtain the list of flows, in addition to the TopN destination providers for that particular flow type. It then also links that to the TopN source address for each individual address highlighted by the TopN destination providers.

It can be used with the following options:
*  --port PORT           The port number you want to search for (default: 80)
*  --provider PROVIDER   The IP of the authorized/trusted server providing the
                        service. Eg: DNS, HTTP, AD servers (default: None)
*  --hours {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24}
                        How many hours to search. 1-24 (default: 1)
*  --filter {eq,ne}      How to search with Provider. Flows equal to that
                        Provider (eq) or not with that Provider (ne) (default:
                        ne)
*  --limit LIMIT         Limit the number of results within the last 24 hours
                        to this value (1-1000) (default: 100)


> Reminder: The -c specifies your credentials .json file that you should have downloaded from your Tetration Platform when enabling the API keys

Sample Usage

Get Flows + TopN /// DNS = 53
```YAML
# python tetration_flow_topN_search.py -c kangaroo_sa_credentials.json -p https://kangaroo.cisco.com --port 53 --limit 500 --hours 24
```

Get Flows + TopN /// DHCP = 67
```YAML
# python tetration_flow_topN_search.py -c kangaroo_sa_credentials.json -p https://kangaroo.cisco.com --port 67 --limit 500 --hours 24
```

Get Flows + TopN /// NTP = 123
```YAML
# python tetration_flow_topN_search.py -c kangaroo_sa_credentials.json -p https://kangaroo.cisco.com --port 123 --limit 500 --hours 24
```


Created by Michael Petrinovic 2018


WARNING:

These scripts are meant for educational/proof of concept purposes only - as demonstrated at Cisco Live and/or my other presentations. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and I am not responsible for any damage or data loss incurred as a result of their use
