from azure.mgmt.eventgrid import EventGridManagementClient

def handle_event_grids(resource, rg, event_grid_client):
    try:
        # Get the Event Grid Topic
        event_grid_topic = event_grid_client.topics.get(rg.name, resource.name)
        print("Getting Event Grid Topic...")

        # Add the keys to the Event Grid Topic dictionary
        event_grid_dict = event_grid_topic.as_dict()

        return event_grid_dict

    except Exception as e:
        return {'Error': str(e)}