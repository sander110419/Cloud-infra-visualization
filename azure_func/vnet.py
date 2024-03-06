from azure.mgmt.network import NetworkManagementClient

def handle_vnet(resource, rg, network_client):
    try:
        # Get the Virtual Network
        vnet = network_client.virtual_networks.get(rg.name, resource.name)
        print("Getting Virtual Network...")

        # Add the keys to the vnet dictionary
        vnet_dict = vnet.as_dict()

        return vnet_dict

    except Exception as e:
        return {'Error': str(e)}