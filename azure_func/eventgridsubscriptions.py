from azure.mgmt.eventgrid import EventGridManagementClient

def handle_event_grid_subscriptions(resource, rg, event_grid_client):
    try:
        # Get the Event Grid Subscription
        event_grid_subscription = event_grid_client.event_subscriptions.get(rg.name, resource.name)
        print("Getting Event Grid Subscription...")

        # Add the keys to the Event Grid Subscription dictionary
        event_grid_dict = event_grid_subscription.as_dict()

        return event_grid_dict

    except Exception as e:
        return {'Error': str(e)}