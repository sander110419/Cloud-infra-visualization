from azure.mgmt.monitor import MonitorManagementClient

def handle_insights_components(resource, rg, monitor_client):
    try:
        # Get the Insights Component
        insights_component = monitor_client.components.get(rg.name, resource.name)
        print("Getting Insights Component...")

        # Add the keys to the insights component dictionary
        insights_component_dict = insights_component.as_dict()

        return insights_component_dict

    except Exception as e:
        return {'Error': str(e)}