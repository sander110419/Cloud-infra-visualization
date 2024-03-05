from azure.mgmt.monitor import MonitorManagementClient

def handle_monitor_action_group(resource, rg, monitor_client):
    try:
        # Get the Action Group
        action_group = monitor_client.action_groups.get(rg.name, resource.name)
        print("Getting Action Group...")

        # Add the keys to the storage account dictionary
        action_group_dict = action_group.as_dict()

        return action_group_dict

    except Exception as e:
        return {'Error': str(e)}