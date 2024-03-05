from azure.mgmt.apimanagement import ApiManagementClient

def handle_api_management(resource, rg, apim_client):
    # Get the API Management
    try:
        # Get the API Management
        api_management = apim_client.api_management_service.get(rg.name, resource.name)
        print("Getting API Management...")

        # Add the keys to the storage account dictionary
        api_management_dict = api_management.as_dict()

        return api_management_dict

    except Exception as e:
        return {'Error': str(e)}