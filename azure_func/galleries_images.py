from azure.mgmt.compute import ComputeManagementClient

def handle_galleries_images(resource, rg, compute_client):
    try:
        # Get the Gallery Image
        gallery_image = compute_client.gallery_images.get(rg.name, resource.name)
        print("Getting Gallery Image...")

        # Add the keys to the Gallery Image dictionary
        gallery_image_dict = gallery_image.as_dict()

        return gallery_image_dict

    except Exception as e:
        return {'Error': str(e)}
