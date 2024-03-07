from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.resource.locks import ManagementLockClient

def handle_management_locks(resource, rg, lock_client):
    try:
        # Get all Management Locks in the resource group
        management_locks = lock_client.management_locks.list_at_resource_group_level(rg)

        print("Getting Management Locks...")
        print(management_locks)

        # Initialize an empty dictionary to store the Management Locks
        management_locks_dict = {}

        # Iterate over the locks
        for lock in management_locks:
            # Convert each lock to a dictionary and add it to the main dictionary
            management_locks_dict[lock.name] = lock.as_dict()

        return management_locks_dict

    except Exception as e:
        return {'Error': str(e)}