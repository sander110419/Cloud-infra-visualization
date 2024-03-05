from azure.mgmt.eventhub import EventHubManagementClient

def handle_event_hub(resource, rg, eventhub_client):
    try:
       # Get the Event Hub
        event_hub = eventhub_client.event_hubs.get(rg.name, resource.name)
        print("Getting Event Hub...")

        # Add the keys to the storage account dictionary
        event_hub_dict = event_hub.as_dict()

        return event_hub_dict

    except Exception as e:
        return {'Error': str(e)}