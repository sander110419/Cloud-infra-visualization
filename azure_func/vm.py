from azure.mgmt.compute import ComputeManagementClient

def handle_virtual_machine(resource, rg, compute_client):
    try:
        # Get the VM
        vm = compute_client.virtual_machines.get(rg.name, resource.name)
        print("Getting VM...")

        # Add the keys to the storage account dictionary
        vm_dict = vm.as_dict()

        return vm_dict

    except Exception as e:
        return {'Error': str(e)}