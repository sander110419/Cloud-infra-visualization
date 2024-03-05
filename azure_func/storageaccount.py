from azure.mgmt.storage import StorageManagementClient
from azure.storage.fileshare import ShareClient
from azure.storage.queue import QueueClient
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient
import uuid

def handle_storage_account(resource, rg, storage_client):

    # Initialize clients for each service using one of the keys
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={resource.name};AccountKey={keys.keys[0].value};EndpointSuffix=core.windows.net"

    share_client = ShareClient.from_connection_string(connection_string)
    queue_client = QueueClient.from_connection_string(connection_string)
    table_service_client = TableServiceClient.from_connection_string(connection_string)
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # Initialize all variables
    storage_account = None
    keys = None
    storage_account_keys = []  # List to store all keys
    storage_account_key_age = None
    properties = None
    storage_account_type = None
    storage_account_redundancy = None
    blob_service_properties = None
    storage_account_https_only = None
    storage_account_public_access = None
    storage_account_blob_public_access = None
    file_service_properties = None
    storage_account_sftp_enabled = None
    storage_account_enable_local_user = None
    network_rule_set = None
    storage_account_tls_version = None
    storage_account_id = None
    file_shares = []
    queues = []
    tables = []
    blob_containers = []
    error_dict = {}
    try:
        # Get the storage account
        storage_account = storage_client.storage_accounts.get_properties(rg.name, resource.name)
        
        # Get the storage account keys
        keys = storage_client.storage_accounts.list_keys(rg.name, resource.name)
        if keys.keys:
            for key in keys.keys:
                storage_account_keys.append({
                    'KeyId': key.key_name,
                    'KeyCreationTime': key.creation_time
                })
        else:
            print("No keys found for this storage account.")


        # Get the storage account properties
        properties = storage_account.sku
        storage_account_type = properties.name
        storage_account_redundancy = properties.tier

        # Get the storage account blob service properties
        blob_service_properties = storage_client.blob_services.get_service_properties(rg.name, resource.name)
        storage_account_https_only = blob_service_properties.default_service_version
        storage_account_public_access = blob_service_properties.delete_retention_policy.enabled
        storage_account_blob_public_access = blob_service_properties.is_versioning_enabled

        # Get the storage account file service properties
        file_service_properties = storage_client.file_services.get_service_properties(rg.name, resource.name)
        storage_account_sftp_enabled = file_service_properties.protocol_settings.smb.multichannel.enabled
        storage_account_enable_local_user = file_service_properties.protocol_settings.smb.authentication_methods

        # Get the storage account network rule set
        network_rule_set = storage_client.storage_accounts.get_network_rule_set(rg.name, resource.name)
        storage_account_tls_version = network_rule_set.minimum_tls_version

        # List all file shares
        file_shares = [share.name for share in share_client.list_shares()]

        # List all queues
        queues = [queue.name for queue in queue_client.list_queues()]

        # List all tables
        tables = [table.name for table in table_service_client.list_tables()]

        # List all blob containers
        blob_containers = [container.name for container in blob_service_client.list_containers()]

    except Exception as e:
        error_dict['PropertiesError'] = str(e)

    print(f"Added Storage Account {storage_account.name}")
    storage_account_id = f"{storage_account.name}_{uuid.uuid4()}"

    return {
        'StorageAccountName': storage_account.name if storage_account else None,
        'StorageAccountLocation': storage_account.location if storage_account else None,
        'StorageAccountRedundancy': storage_account_redundancy,
        'StorageAccountType': storage_account_type,
        'StorageAccountSFTPEnabled': storage_account_sftp_enabled,
        'StorageAccountKeys': storage_account_keys,  # Return the list of keys
        'StorageAccountEnableLocalUser': storage_account_enable_local_user,
        'StorageAccountHttpsOnly': storage_account_https_only,
        'StorageAccountTLSversion': storage_account_tls_version,
        'StorageAccountPublicAccess': storage_account_public_access,
        'StorageAccountBlobPublicAccess': storage_account_blob_public_access,
        'StorageAccountId': storage_account_id,
        'FileShares': file_shares,
        'Queues': queues,
        'Tables': tables,
        'BlobContainers': blob_containers,
        'Errors': error_dict
    }