from azure.mgmt.network import NetworkManagementClient

def handle_network_interface(resource, rg, network_client):
    try:
        # Get the nic
        nic = network_client.network_interfaces.get(rg.name, resource.name)
        print("Getting NIC...")

        # Add the keys to the storage account dictionary
        nic_dict = nic.as_dict()

        return nic_dict

    except Exception as e:
        return {'Error': str(e)}