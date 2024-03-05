from azure.mgmt.signalr import SignalRManagementClient

def handle_signalr_service(resource, rg, signalr_client):
    try:
        # Get the signalr_service
        signalr_service = signalr_client.signal_r.get(rg.name, resource.name)
        print("Getting SignalR Cluster...")

        # Add the keys to the storage account dictionary
        signalr_service_dict = signalr_service.as_dict()

        return signalr_service

    except Exception as e:
        return {'Error': str(e)}