from azure.mgmt.communication import CommunicationServiceManagementClient

def handle_communication_services(resource, rg, communication_client):
    try:
        print("Getting Communication Service...")
        communication_services = communication_client.communication_service.list_by_resource_group(rg.name)
        
        for service in communication_services:
            if service.name == resource.name:
                communication_service_dict = service.as_dict()
                return communication_service_dict

        return {'Error': 'Communication Service not found'}

    except Exception as e:
        return {'Error': str(e)}