from azure.mgmt.compute import ComputeManagementClient

def handle_vm_images(resource, rg, compute_client):
    try:
        # Get the VM Image
        vm_image = compute_client.images.get(rg.name, resource.name)
        print("Getting VM Image...")

        # Add the keys to the VM Image dictionary
        vm_image_dict = vm_image.as_dict()

        return vm_image_dict

    except Exception as e:
        return {'Error': str(e)}