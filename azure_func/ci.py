from azure.mgmt.containerinstance import ContainerInstanceManagementClient

def handle_container_instance(resource, rg, container_instance_client):
    try:
        # Get the container instance
        container_instance = container_instance_client.container_groups.get(rg.name, resource.name)
        print("Getting Container Instance...")

        # Add the keys to the container instance dictionary
        container_instance_dict = container_instance.as_dict()

        return container_instance_dict

    except Exception as e:
        return {'Error': str(e)}