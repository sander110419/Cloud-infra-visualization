from azure.mgmt.dns import DnsManagementClient

def handle_dns_zone(resource, rg, dns_client):
    try:
       # Get the dns_zone
        dns_zone = dns_client.zones.get(rg.name, resource.name)
        print("Getting DNS...")

        # Add the keys to the storage account dictionary
        dns_zone_dict = dns_zone.as_dict()

        return dns_zone_dict

    except Exception as e:
        return {'Error': str(e)}