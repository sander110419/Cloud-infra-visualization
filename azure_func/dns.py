from azure.mgmt.network import NetworkManagementClient

def handle_private_dns_zones(resource, rg, network_client):
    try:
        # Get the Private DNS Zone
        private_dns_zone = network_client.private_dns_zones.get(rg.name, resource.name)
        print("Getting Private DNS Zone...")

        # Add the keys to the Private DNS Zone dictionary
        private_dns_zone_dict = private_dns_zone.as_dict()

        return private_dns_zone_dict

    except Exception as e:
        return {'Error': str(e)}