from azure.mgmt.trafficmanager import TrafficManagerManagementClient

def handle_traffic_manager(resource, rg, traffic_manager_client):
    try:
        # Get the Traffic Manager
        traffic_manager = traffic_manager_client.profiles.get(rg.name, resource.name)
        print("Getting Traffic Manager...")

        # Add the keys to the storage account dictionary
        traffic_manager_dict = traffic_manager.as_dict()

        return traffic_manager_dict

    except Exception as e:
        return {'Error': str(e)}