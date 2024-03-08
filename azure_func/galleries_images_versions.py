from azure.mgmt.compute import ComputeManagementClient

def handle_galleries_images_versions(resource, rg, compute_client):
    try:
        # Get the Gallery Image Version
        gallery_image_version = compute_client.gallery_image_versions.get(rg.name, resource.name)
        print("Getting Gallery Image Version...")

        # Add the keys to the Gallery Image Version dictionary
        gallery_image_version_dict = gallery_image_version.as_dict()

        return gallery_image_version_dict

    except Exception as e:
        return {'Error': str(e)}