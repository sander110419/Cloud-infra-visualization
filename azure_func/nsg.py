from azure.mgmt.network import NetworkManagementClient

def handle_network_security_group(resource, rg, network_client):
    try:
        # Get the Network Security Group
        network_security_group = network_client.network_security_groups.get(rg.name, resource.name)
        print("Getting Network Security Group...")

        # Add the keys to the Network Security Group dictionary
        network_security_group_dict = network_security_group.as_dict()

        return network_security_group_dict

    except Exception as e:
        return {'Error': str(e)}