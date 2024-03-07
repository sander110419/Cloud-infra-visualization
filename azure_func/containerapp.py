from azure.mgmt.containerinstance import ContainerInstanceManagementClient

def handle_container_app(resource, rg, container_client):
    try:
        # Get the Container App
        container_app = container_client.container_groups.get(rg.name, resource.name)
        print("Getting Container App...")

        # Add the keys to the Container App dictionary
        container_app_dict = container_app.as_dict()

        return container_app_dict

    except Exception as e:
        return {'Error': str(e)}