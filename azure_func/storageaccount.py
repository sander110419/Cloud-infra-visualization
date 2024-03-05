from azure.mgmt.storage import StorageManagementClient

def handle_storage_account(resource, rg, storage_client):
    try:
        # Get the storage account
        storage_account = storage_client.storage_accounts.get_properties(rg.name, resource.name)
        print("Getting Storage Account...")

        # Add the keys to the storage account dictionary
        storage_account_dict = storage_account.as_dict()

        return storage_account_dict

    except Exception as e:
        return {'Error': str(e)}