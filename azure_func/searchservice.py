from azure.mgmt.search import SearchManagementClient

def handle_search_service(resource, rg, search_client):
    try:
        # Get the Search Service
        search_service = search_client.services.get(rg.name, resource.name)
        print("Getting Search Service...")

        # Add the keys to the storage account dictionary
        search_service_dict = search_service.as_dict()

        return search_service_dict

    except Exception as e:
        return {'Error': str(e)}