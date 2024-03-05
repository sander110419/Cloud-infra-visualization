from azure.mgmt.trafficmanager import TrafficManagerManagementClient

def handle_load_balancer(resource, rg, network_client):
    try:
       # Get the Load Balancer
        load_balancer = network_client.load_balancers.get(rg.name, resource.name)
        print("Getting Load Balancer...")

        # Add the keys to the storage account dictionary
        load_balancer_dict = load_balancer.as_dict()

        return load_balancer_dict

    except Exception as e:
        return {'Error': str(e)}