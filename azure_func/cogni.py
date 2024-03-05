from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

def handle_cognitive_service(resource, rg, cognitive_client):
    try:
        # Get the cognitive_service
       cognitive_service = cognitive_client.accounts.get(rg.name, resource.name)
       print("Getting Cognitive Service...")

        # Add the keys to the storage account dictionary
       cognitive_service_dict = cognitive_service.as_dict()

       return cognitive_service_dict

    except Exception as e:
        return {'Error': str(e)}