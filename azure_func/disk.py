from azure.mgmt.compute import ComputeManagementClient

def handle_disk(resource, rg, compute_client):
    try:
       # Get the Disk
        disk = compute_client.disks.get(rg.name, resource.name)
        print("Getting Disk...")

        # Add the keys to the storage account dictionary
        disk_dict = disk.as_dict()

        return disk_dict

    except Exception as e:
        return {'Error': str(e)}