from azure.mgmt.eventhub import EventHubManagementClient

def handle_event_hub(resource, rg, eventhub_client):
    try:
       # Get the Event Hub
        namespaces = eventhub_client.namespaces.list_by_resource_group(rg.name)

        print("Getting Event Hub namespaces...")

        # Initialize an empty dictionary to store the Event Hubs
        event_hubs_dict = {}

        # Iterate over the namespaces
        for namespace in namespaces:
            # Get all Event Hubs in the current namespace
            event_hubs = eventhub_client.event_hubs.list_by_namespace(rg.name, namespace.name)

            # Iterate over the Event Hubs
            for event_hub in event_hubs:
                # Convert each Event Hub to a dictionary and add it to the main dictionary
                event_hubs_dict[event_hub.name] = event_hub.as_dict()

        return event_hubs_dict

    except Exception as e:
        return {'Error': str(e)}