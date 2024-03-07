from azure.mgmt.containerregistry import ContainerRegistryManagementClient

def handle_container_registry(resource, rg, container_registry_client):
    try:
        # Get the container registry
        container_registry = container_registry_client.registries.get(rg.name, resource.name)
        print("Getting Container Registry...")

        # Add the keys to the container registry dictionary
        container_registry_dict = container_registry.as_dict()

        return container_registry_dict

    except Exception as e:
        return {'Error': str(e)}