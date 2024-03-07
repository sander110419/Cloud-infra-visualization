from azure.mgmt.network import NetworkManagementClient

def handle_private_endpoint(resource, rg, network_client):
    try:
        # Get the Private Endpoint
        private_endpoint = network_client.private_endpoints.get(rg.name, resource.name)
        print("Getting Private Endpoint...")

        # Add the keys to the Private Endpoint dictionary
        private_endpoint_dict = private_endpoint.as_dict()

        return private_endpoint_dict

    except Exception as e:
        return {'Error': str(e)}