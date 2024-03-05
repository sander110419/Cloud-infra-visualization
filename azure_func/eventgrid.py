from azure.mgmt.eventgrid import EventGridManagementClient

def handle_event_grid(resource, rg, event_grid_client):
    try:
       # Get the Event Grid
        event_grid = event_grid_client.workflows.get(rg.name, resource.name)
        print("Getting Event Grid...")

        # Add the keys to the storage account dictionary
        event_grid_dict = event_grid.as_dict()

        return event_grid_dict

    except Exception as e:
        return {'Error': str(e)}