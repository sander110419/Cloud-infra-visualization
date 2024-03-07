from azure.mgmt.compute import ComputeManagementClient

def handle_vm_snapshot(resource, rg, compute_client):
    try:
        # Get the VM snapshot
        vm_snapshot = compute_client.snapshots.get(rg.name, resource.name)
        print("Getting VM Snapshot...")

        # Add the keys to the snapshot dictionary
        vm_snapshot_dict = vm_snapshot.as_dict()

        return vm_snapshot_dict

    except Exception as e:
        return {'Error': str(e)}