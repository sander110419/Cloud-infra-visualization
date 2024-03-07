from azure.mgmt.logic import LogicManagementClient

def handle_integration_accounts(resource, rg, logic_client):
    try:
        print("Getting Integration Account...")
        integration_account = logic_client.integration_accounts.get(rg.name, resource.name)
        integration_account_dict = integration_account.as_dict()

        return integration_account_dict

    except Exception as e:
        return {'Error': str(e)}