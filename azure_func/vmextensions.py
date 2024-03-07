from azure.mgmt.compute import ComputeManagementClient

def handle_vm_extensions(resource, rg, compute_client):
    try:
        print("Getting Virtual Machines in Resource Group...")
        vms = compute_client.virtual_machines.list(rg)

        all_vm_extensions_details = []
        for vm in vms:
            print(f"Getting Extensions for VM: {vm.name}")
            vm_extensions = compute_client.virtual_machine_extensions.list(
                rg, 
                vm.name
            )

            for extension in vm_extensions:
                extension_detail = compute_client.virtual_machine_extensions.get(
                    rg,
                    vm.name,
                    extension.name
                )
                all_vm_extensions_details.append(extension_detail.as_dict())

        return all_vm_extensions_details

    except Exception as e:
        return {'Error': str(e)}