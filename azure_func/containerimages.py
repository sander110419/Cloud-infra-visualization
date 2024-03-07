from azure.mgmt.containerregistry import ContainerRegistryManagementClient

def handle_container_images(resource, rg, container_registry_client):
    try:
        # Get the Container Image
        container_image = container_registry_client.container_images.get(rg.name, resource.name)
        print("Getting Container Image...")

        # Add the keys to the Container Image dictionary
        container_image_dict = container_image.as_dict()

        return container_image_dict

    except Exception as e:
        return {'Error': str(e)}