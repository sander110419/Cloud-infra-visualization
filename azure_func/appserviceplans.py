from azure.mgmt.web import WebSiteManagementClient

def handle_app_service_plan(resource, rg, web_client):
    try:
        print("Getting app service plan...")
        # Get the app service plan
        app_service_plan = web_client.app_service_plans.get(rg.name, resource.name)

        # Add the keys to the app service plan dictionary
        app_service_plan_dict = app_service_plan.as_dict()

        return app_service_plan_dict

    except Exception as e:
        return {'Error': str(e)}