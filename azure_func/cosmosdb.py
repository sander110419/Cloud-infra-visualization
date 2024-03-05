from azure.mgmt.cosmosdb import CosmosDBManagementClient

def handle_cosmosdb_account(resource, rg, cosmosdb_client):
    try:
        # Get the cosmosdb
       cosmosdb_account = cosmosdb_client.database_accounts.get(rg.name, resource.name)
       print("Getting Cosmos DB...")

        # Add the keys to the storage account dictionary
       cosmosdb_account_dict = cosmosdb_account.as_dict()

       return cosmosdb_account_dict

    except Exception as e:
        return {'Error': str(e)}