readMe = """
Meraki SDK will need to be installed from https://github.com/meraki/dashboard-api-python
You can install the necessary prerequisites using:
pip install -r requirements.txt

This script will backup an origanization's networks, templates, and devices.
Please note that this script will only gather configurations from devices that support API integration.

Depending on how python is installed on your system, you may have to use py, python, or python3 within the command line.
Usage:
    py backupConfigs.py -o <orgId> -k <apiKey> [-t <tag>] [-y]

Please do not hardcode the API key to this script.
It is recommended to instead set the API key as an environmental variable named MERAKI_DASHBOARD_API_KEY.
"""

import asyncio
import csv
from datetime import datetime
import getopt
import argparse
import json
import math
import os
import sys
import meraki
import meraki.aio
import requests
import yaml

backupFileFormat = 'json'
getOperationMappingsFile = 'backupGetOperation.csv'
defaultConfigsDirectory = 'defaults'

orgID = None
totalCalls = 0
defaultConfigs = []
devices = networks = templates = []

# def fileType(file, data, path=''):
#     if path and path[-1] != '/':
#         path += '/'
#     if data:
#         if type(data) != dict or (type(data) == dict and any(data.values())):
#             proceed_saving = False
#             if type(data) == dict and set(data.keys()) ==  {'rfProfileId', 'serial'}:

def backupRun(apiKey, orgId):
    global getOperationMappingsFile, defaultConfigsDirectory, defaultConfigs, orgID, totalCalls

def estimatedTime(apiKey, orgId):
    try:
        dashboard = meraki.DashboardAPI(apiKey, suppress_logging=True)
        networks = dashboard.organizations.getOrganizationNetworks(orgId, total_pages='all')
        templates = dashboard.organizations.getOrganizationConfigTemplates(orgId)
        devices = dashboard.organizations.getOrganizationDevices(orgId, total_pages='all')
        # orgCallLimit = 10
        orgCalls = 19

        totalDevices = len(devices)
        mrDevices = len([d for d in devices if d['model'][:2] == 'MR'])
        msDevices = len([d for d in devices if d['model'][:2] == 'MS'])
        mvDevices = len([d for d in devices if d['model'][:2] == 'MV'])
        mgDevices = len([d for d in devices if d['model'][:2] == 'MG'])
        mxDevices = totalDevices - mrDevices - msDevices - mvDevices - mgDevices
        deviceCalls = (mrDevices + msDevices + mxDevices) + mrDevices + 2 * msDevices + 3 * mvDevices + 2 * mgDevices

        mrNetworks = len([n for n in networks if 'wireless' in n['productTypes']]) + len([t for t in templates if 'wireless' in t['productTypes']])
        msNetworks = len([n for n in networks if 'switch' in n['productTypes']]) + len([t for t in templates if 'switch' in t['productTypes']])
        mxNetworks = len([n for n in networks if 'appliance' in n['productTypes']]) + len([t for t in templates if 'appliance' in t['productTypes']])
        mgNetworks = len([n for n in networks if 'cellularGateway' in n['productTypes']]) + len([t for t in templates if 'cellularGateway' in t['productTypes']])
        mvNetworks = len([n for n in networks if 'camera' in n['productTypes']])
        networkCalls = 19 * mrNetworks + 22 * msNetworks + 32 * mxNetworks + 6 * mgNetworks + 4 * mvNetworks 

        totalCalls = orgCalls + deviceCalls + networkCalls
        minutes = math.ceil(totalCalls / 4 /60)
        return totalCalls, minutes, totalCalls, networkCalls, deviceCalls
    except meraki.APIError:
        sys.exit('Error. Please check API Key and Organization ID combination.')


def printHelp():
    helperLines = readMe.split('\n')
    for line in helperLines:
       print(f'# {line}')


def parseArgs():
    opts = argparse.ArgumentParser(description="Backup Meraki dashboard org, network, templates, and API-compatible devices.")
    opts.add_argument('-o', metavar='<orgId>', nargs=1, help='input organization id (required)', required=True)
    opts.add_argument('-k', metavar='<apiKey>', nargs=1, help='input meraki dashboard api key (required)', required=True)
    opts.add_argument('-a', help="autoruns the script without confirmation", required=False, action='store_true')
    # opts.add_argument('-t') Tag
    args = opts.parse_args()
    return args


def main(arguments):
    if len(arguments) == 0:
        printHelp()
        sys.exit(2)
    else:
        inputs = parseArgs()
        if inputs:
            orgId = inputs.o[0]
            apiKey = inputs.k[0]
            calls, minutes, totalCalls, networkCalls, deviceCalls, = estimatedTime(apiKey, orgId)
            minutes = f'{minutes} minutes' if minutes != 1 else '1 minute'
            message = f'Based on your organization, it is estimated that around {calls:,} API calls will be made, '
            message += f'so should not take longer than about {minutes} to finish running.\n'
            message += 'Do you want to continue? [Y/N]? '
            # message += f'`\n{totalCalls} totalcalls'
            # message += f'\n{networkCalls} networkcalls'
            # message += f'\n{deviceCalls} devicecalls'
            if not inputs.a:
                confirm = input(message)
            if inputs.a or confirm.lower() in ('y', 'yes'):
                print('\n')
                filePath, runTime, madeCalls = backupRun(apiKey, orgId)
                
    

if __name__ == '__main__':
    main(sys.argv[1:])  