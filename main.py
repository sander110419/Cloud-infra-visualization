import uuid
import argparse
import json
import datetime
import time
from azure_func import azure_imports
from azure_func.auth import authenticate
from lxml.etree import Element, SubElement, tostring

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super().default(obj)

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
    'Objects': {}
}

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
        # Initialize an empty dictionary for this subscription
        data['Objects'][subscription] = {}

        #initialize clients
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
        recovery_services_client = azure_imports.RecoveryServicesClient(credential, subscription)
        resource_handlers = {
            'Microsoft.Network/networkInterfaces': (azure_imports.handle_network_interface, network_client),
            'Microsoft.Compute/virtualMachines': (azure_imports.handle_virtual_machine, compute_client),
            'Microsoft.Sql/servers': (azure_imports.handle_sql_server, sql_client),
            'Microsoft.Compute/disks': (azure_imports.handle_disk, compute_client),
            'Microsoft.Web/serverFarms': (azure_imports.handle_app_service_plan, web_client),
            'Microsoft.KeyVault/vaults': (azure_imports.handle_key_vault, keyvault_client),
            'Microsoft.OperationalInsights/workspaces': (azure_imports.handle_log_analytics_workspace, la_client),
            'Microsoft.Storage/storageAccounts': (azure_imports.handle_storage_account, storage_client),
            'Microsoft.ApiManagement/service': (azure_imports.handle_api_management, apim_client),
            'Microsoft.DataLakeStore/accounts': (azure_imports.handle_data_lake_store, datalake_store_client),
            'Microsoft.StreamAnalytics/streamingjobs': (azure_imports.handle_stream_analytics_job, stream_analytics_client),
            'Microsoft.ContainerService/managedClusters': (azure_imports.handle_aks_service, kubernetes_client),
            'Microsoft.Search/searchServices': (azure_imports.handle_search_service, search_client),
            'Microsoft.SignalRService/SignalR': (azure_imports.handle_signalr_service, signalr_client),
            'Microsoft.BotService/botServices': (azure_imports.handle_bot_service, bot_service_client),
            'Microsoft.Devices/IotHubs': (azure_imports.handle_iot_hub, iot_hub_client),
            'Microsoft.CognitiveServices/accounts': (azure_imports.handle_cognitive_service, cognitive_client),
            'Microsoft.Network/dnszones': (azure_imports.handle_dns_zone, dns_client),
            'Microsoft.Cdn/profiles': (azure_imports.handle_cdn_profile, cdn_client),
            'Microsoft.ServiceFabric/clusters': (azure_imports.handle_service_fabric_cluster, sf_client),
            'Microsoft.DevTestLab/schedules': (azure_imports.handle_devtest_lab, devtest_client),
            'Microsoft.Insights/actionGroups' : (azure_imports.handle_monitor_action_group, monitor_client),
            'Microsoft.Scheduler/jobCollections': (azure_imports.handle_scheduler_job_collection, scheduler_client),
            'Microsoft.DocumentDB/databaseAccounts' : (azure_imports.handle_cosmosdb_account, cosmosdb_client),
            'Microsoft.EventGrid/eventSubscriptions': (azure_imports.handle_event_grid, event_grid_client),
            'Microsoft.EventGrid/topics': (azure_imports.handle_event_grid, event_grid_client),
            'Microsoft.RecoveryServices/vaults': (azure_imports.handle_recovery_services_vault, recovery_services_client)
            # 'Microsoft.Network/virtualNetworks': (azure_imports.handle_virtual_network, network_client)
        }

        # Step 3: Get all resource groups
        resource_groups = list(resource_client.resource_groups.list())

        print(f"Found {len(resource_groups)} resource groups")

        for rg in resource_groups:
            # Get resources within the resource group
            resources = list(resource_client.resources.list_by_resource_group(rg.name))

            print(f"Found {len(resources)} resources in resource group {rg.name}")

            # Initialize an empty list for this resource group
            data['Objects'][subscription][rg.name] = []

            # Add each resource to the diagram
            for resource in resources:

                # Get the handler function for this resource type
                handler_info = resource_handlers.get(resource.type)
                if handler_info is not None:
                    handler, client = handler_info
                    # Call the handler function and get the data
                    resource_data = handler(resource, rg, client)

                    data['Objects'][subscription][rg.name].append({
                        'ResourceType': resource.type,
                        'Details': resource_data
                    })

    except Exception as e:
        print(f"An error occurred: {e}")

end_time = time.time()
duration = end_time - start_time

data['Properties']['Duration'] = duration

with open('output.json', 'w') as f:
    json.dump(data, f, cls=CustomEncoder)