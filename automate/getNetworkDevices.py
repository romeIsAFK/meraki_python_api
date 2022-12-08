readMe = """"
v1.0

Depending on OS, use python or python3 to run this script.
This script uses the Meraki library.

Usage:
python getNetworkDevices.py

Notes:
* NEVER hardcode API key to this script, instead place key as an environmental variable named as MERAKI_DASHBOARD_API_KEY.
* This script only uses get requests and is not meant to make modifications to the Meraki Dashboard.
* This script was built to be used with 3.10.7
* Install the Meraki library by using pip install Meraki.
"""

import meraki
import os


def getApiKey():
    return os.getenv('MERAKI_DASHBOARD_API_KEY')


def getOrgId(dashboard):
    organizationDict = {}
    organizationQuery = dashboard.organizations.getOrganizations()
    for organization in organizationQuery:
        organizationDict[organization['name']] = organization['id']
    return organizationDict


def getOrgNets(dashboard, orgId):
    networkList = []
    networksQuery = dashboard.organizations.getOrganizationNetworks(orgId)
    for network in networksQuery:
        networkList.append(network['id'])
    return networkList


def getDevices(dashboard, networkdId):
    DeviceQuery = dashboard.networks.getNetworkDevices(networkdId)
    for device in DeviceQuery:
        if 'name' not in device:
            device['name'] = None
    return DeviceQuery


def main():
    APIKEY = getApiKey()
    dashboard = meraki.DashboardAPI(APIKEY, suppress_logging=True)
    netIdDict = {}
    orgIdDict = getOrgId(dashboard)
    for key in orgIdDict:
        netIdDict[f'Org: {key}, OrgId: {orgIdDict[key]}'] = (getOrgNets(dashboard, orgIdDict[key]))

    deviceList = []
    
    for orgInfo in netIdDict:
        for netId in netIdDict[orgInfo]:
            deviceList.append(getDevices(dashboard, netId))

        print(f'{orgInfo}\n')

        for deviceInfo in deviceList: 
            for device in deviceInfo:
                print(f'NAME: {device["name"]}')
                print(f'MAC: {device["mac"]}')
                print(f'SERIAL: {device["serial"]}')
                print(f'MODEL: {device["model"]}')
                print(f'NETWORK ID: {device["networkId"]}')
                print(f'ADDRESS: {device["address"]}\n')


if __name__ == "__main__":
    main()