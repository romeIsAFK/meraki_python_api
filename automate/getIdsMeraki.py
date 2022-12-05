readMe = """"
v1.0

Depending on OS, use python or python3 to run this script.
This script uses the Meraki library.

Usage:
python getIdMeraki.py

Notes:
* NEVER hardcode API key to this script, instead place key as an environmental variable and name it as MERAKI_DASHBOARD_API_KEY.
* This script only uses get request and is not meant to make modifications to the Meraki Dashboard.
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
    for i in networksQuery:
        networkList.append({'networkName': i['name'], 'networkId': i['id']})
    return networkList


def main():
    API_KEY = getApiKey()
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)
    netIdDict = {}
    orgIdDict = getOrgId(dashboard)
    for key in orgIdDict:
        netIdDict[f'Org: {key}, OrgId: {orgIdDict[key]}'] = (getOrgNets(dashboard, orgIdDict[key]))

    for orgId in netIdDict:
        print(f'{orgId}')
        for orgs in netIdDict[orgId]:
            print(f'Network Name: {orgs["networkName"]}, Network ID:{orgs["networkId"]}')


if __name__ == "__main__":
    main()