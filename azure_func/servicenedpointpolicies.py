from azure.mgmt.network import NetworkManagementClient

def handle_service_endpoint_policy(resource, rg, network_client):
    try:
        print("Getting Service Endpoint Policy...")
        service_endpoint_policy = network_client.service_endpoint_policies.get(rg.name, resource.name)

        # Add the keys to the service endpoint policy dictionary
        service_endpoint_policy_dict = service_endpoint_policy.as_dict()

        return service_endpoint_policy_dict

    except Exception as e:
        return {'Error': str(e)}