from azure.mgmt.web import WebSiteManagementClient

def handle_app_service_plan(resource, rg, web_client):
    try:
        print("Getting app service plan...")
        # Get the app service plan
        app_service_plan = web_client.app_service_plans.get(rg.name, resource.name)

        # Add the keys to the app service plan dictionary
        app_service_plan_dict = app_service_plan.as_dict()

        print("Getting app services...")
        # Get the app services running on the app service plan
        app_services = web_client.web_apps.list_by_resource_group(rg.name, resource.name)
        
        # Convert the app services to a list of dictionaries
        app_services_list = [app_service.as_dict() for app_service in app_services]

        # Add the app services to the app service plan dictionary
        app_service_plan_dict['app_services'] = app_services_list

        return app_service_plan_dict

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'Error': str(e)}