from azure.mgmt.datalake.store import DataLakeStoreAccountManagementClient

def handle_data_lake_store(resource, rg, datalake_store_client):
    try:
       # Get the Data Lake Store
        data_lake_store = datalake_store_client.account.get(rg.name, resource.name)
        print("Getting Data Lake Store...")

        # Add the keys to the storage account dictionary
        data_lake_store_dict = data_lake_store.as_dict()

        return data_lake_store_dict

    except Exception as e:
        return {'Error': str(e)}