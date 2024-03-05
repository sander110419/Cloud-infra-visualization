import uuid
import argparse
import json
import datetime
import time
from azure_func import azure_imports
from azure_func.auth import authenticate
from lxml.etree import Element, SubElement, tostring

# Parse command line arguments
parser = argparse.ArgumentParser(description='Azure authentication parameters')
parser.add_argument('--tenant_id', type=str, required=True, help='Tenant ID')
parser.add_argument('--client_id', type=str, required=True, help='Client ID')
parser.add_argument('--client_secret', type=str, required=True, help='Client Secret')
parser.add_argument('--subscription_id', type=str, required=False, help='Subscription ID')

args = parser.parse_args()

# Initialize JSON file
start_time = time.time()

data = {
    'Properties': {
        'ScriptVersion': '0.1',
        'Datestamp': str(datetime.datetime.now()),
        'Duration': None  # Will be updated at the end of the script
    },
    'Objects': []
}

with open('output.json', 'w') as f:
    json.dump(data, f)

# Authenticate to Azure
tenant_id = args.tenant_id
client_id = args.client_id
client_secret = args.client_secret

credential = azure_imports.authenticate(tenant_id, client_id, client_secret)
subscription_client = azure_imports.SubscriptionClient(credential)

# Use provided subscription ID or get all subscriptions
if args.subscription_id:
    subscriptions = [args.subscription_id]
else:
    subscriptions = [sub.subscription_id for sub in subscription_client.subscriptions.list()]

for subscription in subscriptions:
    try:
        resource_client = azure_imports.ResourceManagementClient(credential, subscription)
        network_client = azure_imports.NetworkManagementClient(credential, subscription)
        compute_client = azure_imports.ComputeManagementClient(credential, subscription)
        la_client = azure_imports.LogAnalyticsManagementClient(credential, subscription)
        storage_client = azure_imports.StorageManagementClient(credential, subscription)
        sql_client = azure_imports.SqlManagementClient(credential, subscription)
        cosmosdb_client = azure_imports.CosmosDBManagementClient(credential, subscription)
        web_client = azure_imports.WebSiteManagementClient(credential, subscription)
        apim_client = azure_imports.ApiManagementClient(credential, subscription)
        datalake_store_client = azure_imports.DataLakeStoreAccountManagementClient(credential, subscription)
        data_factory_client = azure_imports.DataFactoryManagementClient(credential, subscription)
        stream_analytics_client = azure_imports.StreamAnalyticsManagementClient(credential, subscription)
        kubernetes_client = azure_imports.ContainerServiceClient(credential, subscription)
        keyvault_client = azure_imports.KeyVaultManagementClient(credential, subscription)
        search_client = azure_imports.SearchManagementClient(credential, subscription)
        signalr_client = azure_imports.SignalRManagementClient(credential, subscription)
        bot_service_client = azure_imports.AzureBotService(credential, subscription)
        iot_hub_client = azure_imports.IotHubClient(credential, subscription)
        cognitive_client = azure_imports.CognitiveServicesManagementClient(credential, subscription)
        dns_client = azure_imports.DnsManagementClient(credential, subscription)
        cdn_client = azure_imports.CdnManagementClient(credential, subscription)
        sf_client = azure_imports.ServiceFabricManagementClient(credential, subscription)
        devtest_client = azure_imports.DevTestLabsClient(credential, subscription)
        monitor_client = azure_imports.MonitorManagementClient(credential, subscription)
        scheduler_client = azure_imports.SchedulerManagementClient(credential, subscription)
        event_grid_client = azure_imports.EventGridManagementClient(credential, subscription)
        resource_handlers = {
            'Microsoft.Storage/storageAccounts': (azure_imports.handle_storage_account, storage_client),
            'Microsoft.Network/networkInterfaces': azure_imports.handle_network_interface,
            'Microsoft.Compute/virtualMachines': azure_imports.handle_virtual_machine
        }

        # Step 3: Get all resource groups
        resource_groups = list(resource_client.resource_groups.list())

        print(f"Found {len(resource_groups)} resource groups")

        for rg in resource_groups:
            # Get resources within the resource group
            resources = list(resource_client.resources.list_by_resource_group(rg.name))

            print(f"Found {len(resources)} resources in resource group {rg.name}")

            # Add each resource to the diagram
            for resource in resources:
                # Get the handler function for this resource type
                handler_info = resource_handlers.get(resource.type)

                if handler_info is not None:
                    handler, client = handler_info
                    # Call the handler function and get the data
                    resource_data = handler(resource, rg, client)

                    with open('output.json', 'r+') as f:
                        data = json.load(f)
                        data['Objects'].append({
                            'ResourceType': resource.type,
                            'Details': resource_data
                        })
                        f.seek(0)  # Move the cursor back to the beginning of the file
                        json.dump(data, f)
                        f.truncate()  # Remove any remaining part of the old file content

    except Exception as e:
        print(f"An error occurred: {e}")

end_time = time.time()
duration = end_time - start_time

with open('output.json', 'r+') as f:
    data = json.load(f)
    data['Properties']['Duration'] = duration
    f.seek(0)  # Move the cursor back to the beginning of the file
    json.dump(data, f)
    f.truncate()  # Remove any remaining part of the old file content