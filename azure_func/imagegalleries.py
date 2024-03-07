from azure.mgmt.compute import ComputeManagementClient

def handle_image_galleries(resource, rg, compute_client):
    try:
        # Get the Image Gallery
        image_gallery = compute_client.galleries.get(rg.name, resource.name)
        print("Getting Image Gallery...")

        # Add the keys to the Image Gallery dictionary
        image_gallery_dict = image_gallery.as_dict()

        return image_gallery_dict

    except Exception as e:
        return {'Error': str(e)}