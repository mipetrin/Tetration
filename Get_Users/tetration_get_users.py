#! /usr/bin/env python
"""
Simple script to allow a user to obtain the list of all Users defined on the Tetration Platform

Requires the Tetration API Client: pip install tetpyclient

TO DO:
    * Retrieve what each user role is
    * Retrieve what scopes they are assigned to

Michael Petrinovic 2018
"""
import traceback
from tetpyclient import RestClient
import requests.packages.urllib3
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tabulate import tabulate

def get_users(session):
    """
    Tetration API call for Users
    """
    resp = session.get('/openapi/v1/users')
    user_list = []

    for entry in resp.json():
        user_list.append((entry['id'], entry['first_name'], entry['last_name'], entry['email']))

    return user_list

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
        users = get_users(RC_SESSION)
        # Print out all the data collected
        print ("\n")
        print (tabulate(users, headers = ["ID", "First Name", "Last Name", "Email"], tablefmt="orgtbl"))

        summary = "Total users: " + str(len(users))
        print "=" * len(summary)
        print summary
        print "=" * len(summary)

    except Exception, err:
        print "Operation failed"
        print traceback.format_exc(err)


if __name__ == '__main__':
    main()
