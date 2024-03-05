from azure.mgmt.servicebus import ServiceBusManagementClient

def handle_service_bus(resource, rg, servicebus_client):
    try:
        # Get the service_bus
        service_bus = servicebus_client.namespaces.get(rg.name, resource.name)
        print("Getting Service Bus...")

        # Add the keys to the storage account dictionary
        service_bus_dict = service_bus.as_dict()

        return service_bus_dict

    except Exception as e:
        return {'Error': str(e)}