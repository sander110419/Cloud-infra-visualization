from azure.mgmt.network import NetworkManagementClient

def handle_private_link_services(resource, rg, network_client):
    try:
        print("Getting Private Link Service...")
        private_link_service = network_client.private_link_services.get(rg.name, resource.name)
        private_link_service_dict = private_link_service.as_dict()

        return private_link_service_dict

    except Exception as e:
        return {'Error': str(e)}