import meraki
import os

api_key = os.getenv('MERAKI_DASHBOARD_API_KEY')
org_id = os.getenv('MERAKI_ORG_ID')
dashboard = meraki.DashboardAPI(api_key)


def get_organizational_ids():
    return dashboard.organizations.getOrganizations()


def get_network_ids(arg):
    return dashboard.organizations.getOrganizationNetworks(arg)


print(get_organizational_ids())


