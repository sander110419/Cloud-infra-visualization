from azure.mgmt.compute import ComputeManagementClient

def handle_vm_scale_set(resource, rg, compute_client):
    try:
        # Get the Virtual Machine Scale Set
        vm_scale_set = compute_client.virtual_machine_scale_sets.get(rg.name, resource.name)
        print("Getting Virtual Machine Scale Set...")

        # Add the keys to the VM Scale Set dictionary
        vm_scale_set_dict = vm_scale_set.as_dict()

        return vm_scale_set_dict

    except Exception as e:
        return {'Error': str(e)}