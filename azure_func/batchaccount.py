from azure.mgmt.batch import BatchManagementClient

def handle_batch_account(resource, rg, batch_client):
    try:
        # Get the Batch Account
        batch_account = batch_client.batch_account.get(rg.name, resource.name)
        print("Getting Batch Account...")

        # Add the keys to the storage account dictionary
        batch_account_dict = batch_account.as_dict()

        return batch_account_dict

    except Exception as e:
        return {'Error': str(e)}