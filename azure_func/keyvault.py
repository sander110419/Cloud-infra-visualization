from azure.mgmt.keyvault import KeyVaultManagementClient

def handle_key_vault(resource, rg, kv_client):
    try:
       # Get the key_vault
        key_vault = kv_client.vaults.get(rg.name, resource.name)
        print("Getting Key Vault...")

        # Add the keys to the storage account dictionary
        key_vault_dict = key_vault.as_dict()

        return key_vault_dict

    except Exception as e:
        return {'Error': str(e)}