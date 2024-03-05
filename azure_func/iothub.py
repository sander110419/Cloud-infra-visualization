from azure.mgmt.iothub import IotHubClient

def handle_iot_hub(resource, rg, iot_hub_client):
    try:
       # Get the IoT Hub
        iot_hub = iot_hub_client.iot_hub_resource.get(rg.name, resource.name)
        print("Getting IoT Hub...")

        # Add the keys to the storage account dictionary
        iot_hub_dict = iot_hub.as_dict()

        return iot_hub_dict

    except Exception as e:
        return {'Error': str(e)}