from azure.mgmt.logic import LogicManagementClient

def handle_logic_app(resource, rg, logic_client):
    try:
        # Get the Logic App
        logic_app = logic_client.workflows.get(rg.name, resource.name)
        print("Getting Logic App...")

        # Add the keys to the storage account dictionary
        logic_app_dict = logic_app.as_dict()

        return logic_app_dict

    except Exception as e:
        return {'Error': str(e)}