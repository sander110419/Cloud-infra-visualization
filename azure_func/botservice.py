from azure.mgmt.botservice import AzureBotService

def handle_bot_service(resource, rg, bot_service_client):
    try:
        # Get the Bot Service
        bot_service = bot_service_client.bots.get(rg.name, resource.name)
        print("Getting Bot Service...")

        # Add the keys to the storage account dictionary
        bot_service_dict = bot_service.as_dict()

        return bot_service_dict

    except Exception as e:
        return {'Error': str(e)}