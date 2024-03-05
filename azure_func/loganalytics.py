from azure.mgmt.loganalytics import LogAnalyticsManagementClient


def handle_log_analytics_workspace(resource, rg, la_client):
    try:
        # Get the log analytics workspace
        log_analytics_workspace = la_client.workspaces.get(rg.name, resource.name)
        print("Getting log analytics workspace...")

        # Add the keys to the storage account dictionary
        log_analytics_workspace_dict = log_analytics_workspace.as_dict()

        return log_analytics_workspace_dict

    except Exception as e:
        return {'Error': str(e)}