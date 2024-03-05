from azure.mgmt.datafactory import DataFactoryManagementClient

def handle_data_factory(resource, rg, data_factory_client):
    try:
        # Get the Data Factory
        data_factory = data_factory_client.factories.get(rg.name, resource.name)
        print("Getting Data Factory...")

        # Add the keys to the storage account dictionary
        data_factory_dict = data_factory.as_dict()

        return data_factory_dict

    except Exception as e:
        return {'Error': str(e)}