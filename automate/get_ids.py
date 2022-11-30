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
    for organization in orgInfo:
        organizationDictionary[organization["name"]] = organization["id"]
    return organizationDictionary


def getNetworkID(organizationDictionary):
    orgDictionary = {}
    for orgID in organizationDictionary:
        queryURL = URL + f"/organizations/{organizationDictionary[orgID]}/networks"
        response = requests.get(queryURL, headers= APIKEY)
        networkInfo = json.loads(response.text)
        for network in networkInfo:
            orgDictionary[network["name"]] = network["id"]
    return orgDictionary


if __name__ == "__main__":
    orgID = getOrgID()
    networks = getNetworkID(orgID)
    print(f'Organization name: {orgID}: {networks}')
