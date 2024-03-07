from azure.mgmt.servicebus import ServiceBusManagementClient

def handle_service_bus_queues(resource, rg, servicebus_client):
    try:
        # Get all Service Bus namespaces in the resource group
        namespaces = servicebus_client.namespaces.list_by_resource_group(rg)

        print("Getting Service Bus namespaces...")

        # Initialize an empty dictionary to store the Service Bus Queues
        service_bus_queues_dict = {}

        # Iterate over the namespaces
        for namespace in namespaces:
            # Get all Service Bus Queues in the current namespace
            queues = servicebus_client.queues.list_by_namespace(rg, namespace.name)
            # Iterate over the Queues
            for queue in queues:
                # Convert each Queue to a dictionary and add it to the main dictionary
                service_bus_queues_dict[queue.name] = queue.as_dict()

        return service_bus_queues_dict

    except Exception as e:
        return {'Error': str(e)}