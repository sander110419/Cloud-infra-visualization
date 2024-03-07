from azure.mgmt.network import NetworkManagementClient

def handle_public_ip(resource, rg, network_client):
    try:
        print("Getting Public IP Address...")
        # Get the public ip address
        public_ip = network_client.public_ip_addresses.get(rg.name, resource.name)

        # Add the keys to the public ip address dictionary
        public_ip_dict = public_ip.as_dict()

        return public_ip_dict

    except Exception as e:
        return {'Error': str(e)}