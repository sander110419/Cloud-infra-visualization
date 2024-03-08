from azure.mgmt.monitor import MonitorManagementClient

def handle_insights_scheduled_query_rules(resource, rg, monitor_client):
    try:
        # Get the Scheduled Query Rule
        scheduled_query_rule = monitor_client.scheduled_query_rules.get(rg.name, resource.name)
        print("Getting Scheduled Query Rule...")

        # Add the keys to the scheduled query rule dictionary
        scheduled_query_rule_dict = scheduled_query_rule.as_dict()

        return scheduled_query_rule_dict

    except Exception as e:
        return {'Error': str(e)}