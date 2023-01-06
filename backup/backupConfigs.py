readMe = """
Meraki SDK will need to be installed from https://github.com/meraki/dashboard-api-python
-or-
You can install the necessary prerequisites using:
pip install -r requirements.txt

This script will backup an origanization's networks, templates, and devices.
Please note that this script will only gather configurations from devices that support API integration.

Depending on how python is installed on your system, you may have to use py, python, or python3 within the command line.
Usage:
    py backupConfigs.py -o <orgId> -k <apiKey> [-t <tag>] [-y]

Please do not hardcode an API key to this script.
It is recommended to instead set the API key as an environmental variable named MERAKI_DASHBOARD_API_KEY if defining a variable value is necessary.
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

ORGID = None
TOTALCALLS = 0
COMPLETEDOPERATIONS = set()
DEFAULTCONFIGS = []
DEVICES = NETWORKS = TEMPLATES = []

# def fileType(file, data, path=''):
#     if path and path[-1] != '/':
#         path += '/'
#     if data:
#         if type(data) != dict or (type(data) == dict and any(data.values())):
#             proceed_saving = False
#             if type(data) == dict and set(data.keys()) ==  {'rfProfileId', 'serial'}:


def generateFileName(operation):
    return 0
    #NEEDS WORK

async def backupOrg(dashboard, endpoints):
    calls = []

    for endpoint in endpoints:
        logic = endpoint['Logic']
        operation = endpoint['operationId']
        fileName = generateFileName(operation)
        tags = eval(endpoint['tag'])
        scope = generateScope(tags)
        functionalCall = f'dashboard.{scope}.{operation}(ORGID)'
        
        if operation.startswith('getOrganization') and logic not in ('skipped', 'script'):
            params = [p['name'] for p in eval(endpoint['parameters'])]
            if 'perPage' in params:
                functionalCall = functionalCall[:-1] + ",totalPages='all')"
            
            calls.append(
                {
                    'operation': operation,
                    'functionCall': functionalCall,
                    'fileName': fileName,
                    'filePath':'',
                }
            )
    await makeCalls(dashboard, calls)
    #NEEDS WORK

async def backupDevices(dashboard, endpoints, networks, devices):
    return 0
    #NEEDS WORK

async def backupApplianceVlans(dashboard, networks):
    return 0
    #NEEDS WORK

async def backupMsProfiles(dashboard, templates):
    return 0
    #NEEDS WORK

async def backupMsProfilePorts(dashboard, templates):
    return 0
    #NEEDS WORK

async def backupMrSsids(dashboard, endpoints, network):
    return 0
    #NEEDS WORK

async def backupBleSettings(dashboard, networks, devices):
    return 0
    #NEEDS WORK


async def mainAsync(apiKey, operations, endpoints):
    global DEVICES, NETWORKS, TEMPLATES
    async with meraki.aio.AsyncDashboardAPI(apiKey, maximum_concurrent_requests=3, maximum_retries=4, print_console=True, suppress_logging=False) as dashboard:
        
        await backupOrg(dashboard, endpoints)

        await backupDevices(dashboard, endpoints, NETWORKS + TEMPLATES, DEVICES)

        await backupApplianceVlans(dashboard, NETWORKS + TEMPLATES)

        await backupMsProfiles(dashboard, TEMPLATES)

        await backupMsProfilePorts(dashboard, TEMPLATES)

        await backupMrSsids(dashboard, NETWORKS + TEMPLATES)

        await backupBleSettings(dashboard, NETWORKS, DEVICES)
    
    for endpoint in endpoints:
        if endpoint['Logic'] == 'skipped':
            operation = endpoint['operationId']
            COMPLETEDOPERATIONS.add(operation)
    unfinished = [operation for operation in operations if operation['operationId'] not in COMPLETEDOPERATIONS]
    if unfinished:
        print(f'{len(unfinished)} API endpoints that were not called during this backup process:')
        for operation in unfinished:
            print(operation['operationId'])


def backupRun(apiKey, orgId):
    global GETOPERATIONSMAPPINGSFILE, DEFAULTCONFIGSDIRECTORY, DEFAULTCONFIGS, ORGID, TOTALCALLS

    start = datetime.now()
    APIKEY = {"X-Cisco-Meraki-API-Key": apiKey}
    spec = requests.get('https://api.meraki.com/api/v1/openapiSpec', headers=APIKEY).json()
    currentOperations = []

    for uri in spec['paths']:
        methods = spec['paths'][uri]
        if 'get' in methods and ('post' or 'put' in methods):
            currentOperations.append(spec['paths'][uri]['get'])

    outputFile = open('currentGetOperations.csv', mode = 'w', newline='\n')
    fieldNames = ['operationId', 'tags', 'description', 'parameters']
    csvWriter = csv.DictWriter(outputFile, fieldNames, quoting=csv.QUOTE_ALL, extrasaction='ignore')
    csvWriter.writeheader()
    for ops in currentOperations:
        csvWriter.writerow(ops)
    outputFile.close()
    
    inputMappings = []
    with open(GETOPERATIONSMAPPINGSFILE, encoding='utf-8-sig') as fp:
        csvReader = csv.DictReader(fp)
        for row in csvReader:
            inputMappings.append(row)

    os.chdir(DEFAULTCONFIGSDIRECTORY)
    files = os.listdir()
    for file in files:
        if '.json' in file:
            with open(file) as fp:
                data = json.load(fp)
            DEFAULTCONFIGS.append(data)

    os.chdir('..')

    currentTime = datetime.now()
    backupPath = f'backup_{orgId}_{currentTime:%Y-%m-%d_%H-%M-%S}'
    os.mkdir(backupPath)
    os.chdir(backupPath)

    #Start of the backup
    ORGID = orgId
    backupLoop = asyncio.get_event_loop()
    backupLoop.run_until_complete(mainAsync(apiKey,currentOperations, inputMappings))

    #End of backup
    end = datetime.now()
    timeRan = end - start
    return backupPath, timeRan, TOTALCALLS


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
            calls, minutes = estimatedTime(apiKey, orgId)
            minutes = f'{minutes} minutes' if minutes != 1 else '1 minute'
            message = f'Based on your organization, it is estimated that around {calls:,} API calls will be made, '
            message += f'so the script should not take longer than about {minutes} to complete.\n'
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