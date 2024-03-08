from azure.mgmt.monitor import MonitorManagementClient

def handle_insights_metric_alerts(resource, rg, monitor_client):
    try:
        # Get the Metric Alert
        metric_alert = monitor_client.metric_alerts.get(rg.name, resource.name)
        print("Getting Metric Alert...")

        # Add the keys to the metric alert dictionary
        metric_alert_dict = metric_alert.as_dict()

        return metric_alert_dict

    except Exception as e:
        return {'Error': str(e)}