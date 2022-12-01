readMe = """
v1.1 

Depending on OS, use python or python3 to run this script.

Usage:
    python getids.py

Notes:
* NEVER hardcode API key to this script, instead place key as an environmental variable and name it as MERAKI_DASHBOARD_API_KEY.
* This script only only uses get request and is not meant to make modifications to the Meraki Dashboard.
* This script was built to be used with 3.10.7
"""

import requests
import json
import os

URL = "https://api.meraki.com/api/v1"
APIKEY = {"X-Cisco-Meraki-API-Key": os.getenv("MERAKI_DASHBOARD_API_KEY")}


def getOrgID():
    queryURL = URL + "/organizations"
    response = requests.get(queryURL, headers=APIKEY)
    orgInfo = json.loads(response.text)
    organizationDictionary = {}
    organizationList = []
    for organization in orgInfo:
        organizationDictionary[organization["name"]] = organization["id"]
        organizationList.append(organizationDictionary)
    return organizationList


def getNetworkID(organizationList):
    orgDictionary = {}
    networkList = []
    for orgInfo in organizationList:
        for orgName in orgInfo:
            queryURL = URL + f"/organizations/{orgInfo[orgName]}/networks"
            response = requests.get(queryURL, headers= APIKEY)
            networkInfo = json.loads(response.text)
            for info in networkInfo:
                networkList.append(f'Name: {info["name"]}, ID = {info["id"]}')
            orgDictionary[f'Organization name: {orgName}, ID: {orgInfo[orgName]}'] = networkList
    return orgDictionary


if __name__ == "__main__":
    orgID = getOrgID()
    networks = getNetworkID(orgID)
    for network in networks:
        print(f'{network}, Networks: {networks[network]}')