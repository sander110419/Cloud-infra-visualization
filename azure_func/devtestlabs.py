from azure.mgmt.devtestlabs import DevTestLabsClient

def handle_devtest_lab(resource, rg, devtest_client):
    try:
       # Get the devtest_lab
        devtest_lab = devtest_client.labs.get(rg.name, resource.name)
        print("Getting Devtest Lab...")


        # Add the keys to the storage account dictionary
        devtest_lab_dict = devtest_lab.as_dict()

        return devtest_lab_dict

    except Exception as e:
        return {'Error': str(e)}