from azure.mgmt.storagesync import MicrosoftStorageSync

def handle_storage_sync_services(resource, rg, storage_sync_client):
    try:
        print("Getting Storage Sync Service...")
        storage_sync_service = storage_sync_client.storage_sync_services.get(rg.name, resource.name)
        storage_sync_service_dict = storage_sync_service.as_dict()

        return storage_sync_service_dict

    except Exception as e:
        return {'Error': str(e)}