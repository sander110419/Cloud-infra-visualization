from azure.mgmt.web import WebSiteManagementClient

def handle_appservices(resource, rg, web_client):
    try:
        # Get the app services
        app_services = web_client.web_apps.get(rg.name, resource.name)
        print("Getting SQL Database...")

        # Add the details to the app service dictionary
        app_services_dict = app_services.as_dict()

        return app_services_dict

    except Exception as e:
        return {'Error': str(e)}