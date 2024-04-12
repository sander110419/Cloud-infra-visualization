import json
import time
import os
import logging
from output_xlsx import output_to_excel
from functions import set_up_logging, parse_arguments, initialize_data, authenticate_to_azure, get_subscriptions, CustomEncoder
from azure_func import azure_imports
from tqdm import tqdm
from azure_func.resource_functions import *

#parse arguments
args = parse_arguments()
#set up logging
set_up_logging(args.log_level)
#initialise data
data, start_time = initialize_data()
#authenticate to Azure
credential, subscription_client = authenticate_to_azure(args.tenant_id, args.client_id, args.client_secret)
#Get all subscriptions from erguments
subscriptions = get_subscriptions(subscription_client, args.subscription_id)

# Define a dictionary mapping client names to their corresponding classes
client_classes = {
    'network': azure_imports.NetworkManagementClient,
    'compute': azure_imports.ComputeManagementClient,
    'log_analytics': azure_imports.LogAnalyticsManagementClient,
    'storage': azure_imports.StorageManagementClient,
    'sql': azure_imports.SqlManagementClient,
    'cosmosdb': azure_imports.CosmosDBManagementClient,
    'web': azure_imports.WebSiteManagementClient,
    'api_management': azure_imports.ApiManagementClient,
    'data_lake_store': azure_imports.DataLakeStoreAccountManagementClient,
    'data_factory': azure_imports.DataFactoryManagementClient,
    'stream_analytics': azure_imports.StreamAnalyticsManagementClient,
    'kubernetes': azure_imports.ContainerServiceClient,
    'keyvault': azure_imports.KeyVaultManagementClient,
    'search': azure_imports.SearchManagementClient,
    'signalr': azure_imports.SignalRManagementClient,
    'bot_service': azure_imports.AzureBotService,
    'iot_hub': azure_imports.IotHubClient,
    'cognitive': azure_imports.CognitiveServicesManagementClient,
    'dns': azure_imports.DnsManagementClient,
    'cdn': azure_imports.CdnManagementClient,
    'service_fabric': azure_imports.ServiceFabricManagementClient,
    'devtest': azure_imports.DevTestLabsClient,
    'monitor': azure_imports.MonitorManagementClient,
    'scheduler': azure_imports.SchedulerManagementClient,
    'event_grid': azure_imports.EventGridManagementClient,
    'recovery_services': azure_imports.RecoveryServicesClient,
    'container': azure_imports.ContainerInstanceManagementClient,
    'containerapp': azure_imports.ContainerAppsAPIClient,
    'eventhub': azure_imports.EventHubManagementClient,
    'logic': azure_imports.LogicManagementClient,
    'container_registry': azure_imports.ContainerRegistryManagementClient,
    'lock': azure_imports.ManagementLockClient,
    'servicebus': azure_imports.ServiceBusManagementClient,
    'container_instance': azure_imports.ContainerInstanceManagementClient,
    'storage_sync': azure_imports.MicrosoftStorageSync,
    'communication': azure_imports.CommunicationServiceManagementClient,
    'alertsmanagement': azure_imports.AlertsManagementClient,
    'datamigration': azure_imports.DataMigrationManagementClient,
    'recovery_backup_items': azure_imports.RecoveryServicesBackupClient
}
total_resources = 0

for subscription in subscriptions:
    resource_client = azure_imports.ResourceManagementClient(credential, subscription)
    try:
        # Initialize an empty dictionary for this subscription
        data['Objects'][subscription] = {}

        # Initialize clients
        clients = {name: cls(credential, subscription) for name, cls in client_classes.items()}

        resource_handlers = {
            # ... (same as before) ...
        }

        # Step 3: Get all resource groups
        resource_groups = list(resource_client.resource_groups.list())

        logging.info(f"Found {len(resource_groups)} resource groups")

        for rg in resource_groups:
            # Get resources within the resource group
            resources = list(resource_client.resources.list_by_resource_group(rg.name))

            logging.info(f"Found {len(resources)} resources in resource group {rg.name}")

            total_resources += len(resources)

            # Initialize an empty list for this resource group
            data['Objects'][subscription][rg.name] = []

    except Exception as e:
        logging.info(f"An error occurred: {e}")

with tqdm(total=total_resources) as pbar:

    for subscription in subscriptions:
        resource_client = azure_imports.ResourceManagementClient(credential, subscription)
        try:
            # Initialize an empty dictionary for this subscription
            data['Objects'][subscription] = {}

            # Initialize clients
            clients = {name: cls(credential, subscription) for name, cls in client_classes.items()}

            resource_handlers = {
                'Microsoft.Network/networkInterfaces': [(handle_network_interface, 'network')],
                'Microsoft.Compute/virtualMachines': [
                    (handle_virtual_machine, 'compute'),
                    (handle_virtual_machines_extensions, 'compute')
                ],
                'Microsoft.Compute/virtualMachineScaleSets': [(handle_vm_scale_set, 'compute')],
                'Microsoft.Sql/servers': [(handle_sql_server, 'sql')],
                'Microsoft.Sql/servers/databases': [(handle_sql_db, 'sql')],
                'Microsoft.Compute/disks': [(handle_disk, 'compute')],
                'Microsoft.Web/serverFarms': [(handle_app_service_plan, 'web')],
                'Microsoft.Web/sites': [(handle_appservices, 'web')],
                'Microsoft.KeyVault/vaults': [(handle_key_vault, 'keyvault')],
                'Microsoft.OperationalInsights/workspaces': [(handle_log_analytics_workspace, 'log_analytics')],
                'Microsoft.Storage/storageAccounts': [(handle_storage_account, 'storage')],
                'Microsoft.ApiManagement/service': [(handle_api_management, 'api_management')],
                'Microsoft.DataLakeStore/accounts': [(handle_data_lake_store, 'datalake_store')],
                'Microsoft.StreamAnalytics/streamingjobs': [(handle_stream_analytics_job, 'stream_analytics')],
                'Microsoft.ContainerService/managedClusters': [(handle_aks_service, 'kubernetes')],
                'Microsoft.Search/searchServices': [(handle_search_service, 'search')],
                'Microsoft.SignalRService/SignalR': [(handle_signalr_service, 'signalr')],
                'Microsoft.BotService/botServices': [(handle_bot_service, 'bot_service')],
                'Microsoft.Devices/IotHubs': [(handle_iot_hub, 'iot_hub')],
                'Microsoft.CognitiveServices/accounts': [(handle_cognitive_service, 'cognitive')],
                #'Microsoft.Network/privateDnsZones': [(handle_private_dns_zones, 'network')],
                'Microsoft.Cdn/profiles': [(handle_cdn_profile, 'cdn')],
                'Microsoft.ServiceFabric/clusters': [(handle_service_fabric_cluster, 'service_fabric')],
                'Microsoft.DevTestLab/schedules': [(handle_devtest_lab, 'devtest')],
                'Microsoft.Insights/actionGroups' : [(handle_monitor_action_group, 'monitor')],
                'Microsoft.Scheduler/jobCollections': [(handle_scheduler_job_collection, 'scheduler')],
                'Microsoft.DocumentDb/databaseAccounts' : [(handle_cosmosdb_account, 'cosmosdb')],
                'Microsoft.EventGrid/eventSubscriptions': [(handle_event_grid_subscriptions, 'event_grid')],
                'Microsoft.EventGrid/topics': [(handle_event_grids, 'event_grid')],
                'Microsoft.RecoveryServices/vaults': [
                    (handle_recovery_services_vault, 'recovery_services'),
                    (handle_recovery_services_vault_items, 'recovery_backup_items')
                ],
                'Microsoft.Network/virtualNetworks': [(handle_vnet, 'network')],
                'Microsoft.Network/virtualNetworks/subnets': [(handle_all_subnets, 'network')],
                'Microsoft.Network/privateEndpoints': [(handle_private_endpoint, 'network')],
                'Microsoft.Compute/proximityPlacementGroups': [(handle_proximity_placement_group, 'compute')],
                'Microsoft.Network/networkSecurityGroups': [(handle_network_security_group, 'network')],
                'Microsoft.App/containerApps': [(handle_container_app, 'containerapp')],
                'Microsoft.EventHub/namespaces': [
                    (handle_event_hub_namespaces, 'eventhub'),
                    (handle_event_hub_instance, 'eventhub')
                ],
                'Microsoft.Logic/workflows': [(handle_logic_app, 'logic')],
                'Microsoft.ContainerRegistry/registries' : [(handle_container_registry, 'container_registry')],
                #'Microsoft.ServiceBus/namespaces' : [(handle_service_bus_queues, 'servicebus')],
                'Microsoft.Authorization/locks' : [(handle_management_locks, 'lock')],
                'Microsoft.ContainerInstance/containerGroups' : [(handle_container_instance, 'container_instance')],
                'Microsoft.Network/loadBalancers' : [(handle_load_balancer, 'network')],
                'Microsoft.DataFactory/factories' : [(handle_data_factory, 'data_factory')],
                'Microsoft.Compute/galleries' : [(handle_image_galleries, 'compute')],
                'Microsoft.Compute/images' : [(handle_vm_images, 'compute')],
                'Microsoft.Compute/snapshots' : [(handle_vm_snapshot, 'compute')],
                'Microsoft.Network/publicIPAddresses' : [(handle_public_ip, 'network')],
                'Microsoft.Web/certificates' : [(handle_web_certificate, 'web')],
                'Microsoft.Web/connections' : [(handle_web_connections, 'web')],
                'Microsoft.StorageSync/storageSyncServices' : [(handle_storage_sync_services, 'storage_sync')],
                #'Microsoft.Sql/managedInstances' : [(handle_sql_managed_instances, 'sql')],
                'Microsoft.Network/privateLinkServices' : [(handle_private_link_services, 'network')],
                'Microsoft.Logic/integrationAccounts' : [(handle_integration_accounts, 'logic')],
                'Microsoft.Communication/CommunicationServices' : [(handle_communication_services, 'communication')],
                'Microsoft.Sql/virtualCluster' : [(handle_virtual_cluster, 'sql')],
                'Microsoft.Compute/restorePointCollections' : [(handle_restore_point_collections, 'compute')],
                #'Microsoft.Sql/managedInstances/databases' : [(handle_sql_managed_instances_db, 'sql')],
                'Microsoft.DataMigration/SqlMigrationServices' : [(handle_sql_migration_services, 'datamigration')],
                'Microsoft.Network/serviceEndpointPolicies' : [(handle_service_endpoint_policy, 'network')],
                #'Microsoft.Insights/components' : [(handle_insights_components, 'monitor')],
                'Microsoft.Insights/metricalerts' : [(handle_insights_metric_alerts, 'monitor')],
                'Microsoft.Insights/scheduledqueryrules' : [(handle_insights_scheduled_query_rules, 'monitor')],
                #'Microsoft.Network/applicationGatewayWebApplicationFirewallPolicies' : [(handle_application_gateway_waf_policies, 'network')],
                # 'Microsoft.Cdn/profiles/afdendpoints' : [(handle_afd_endpoints, 'cdn')],
                'Microsoft.Network/routeTables' : [(handle_route_tables, 'network')],
                'Microsoft.Compute/galleries/images' : [(handle_galleries_images, 'compute')],
                'Microsoft.Compute/galleries/images/versions' : [(handle_galleries_images_versions, 'compute')],
                'microsoft.alertsmanagement/smartDetectorAlertRules' : [(handle_smart_detector_alert_rules, 'alertsmanagement')],
                'Microsoft.AlertsManagement/actionRules' : [(handle_action_rules, 'alertsmanagement')]
            }

            # Step 3: Get all resource groups
            resource_groups = list(resource_client.resource_groups.list())

            logging.info(f"Found {len(resource_groups)} resource groups")

            for rg in resource_groups:
                # Get resources within the resource group
                resources = list(resource_client.resources.list_by_resource_group(rg.name))

                logging.info(f"Found {len(resources)} resources in resource group {rg.name}")

                # Initialize an empty list for this resource group
                data['Objects'][subscription][rg.name] = []

                # Add each resource to the diagram
                for resource in resources:
                    #logging.info(resource.type)

                    # Get the handler functions for this resource type
                    logging.info(f"Processing resource {resource.name} of type {resource.type}")
                    handler_infos = resource_handlers.get(resource.type)
                    if handler_infos is not None:
                        for handler_info in handler_infos:
                            handler, client_key = handler_info
                            client = clients[client_key]
                            # Call the handler function and get the data
                            resource_data = handler(resource, rg, client)
                            if 'Error' in resource_data:
                                logging.info(f"Error in {handler.__name__}: {resource_data['Error']}")
                            #else:
                            #    logging.info(f"Finished calling {handler.__name__} for resource {resource.name}")

                            data['Objects'][subscription][rg.name].append({
                                'ResourceType': resource.type,
                                'Details': resource_data
                            })
                    #update progress bar
                    pbar.update()

        except Exception as e:
            logging.info(f"An error occurred: {e}")

#record endtime for json properties
end_time = time.time()
duration = end_time - start_time

data['Properties']['Duration'] = duration

# Get output folder from arguments
output_folder = args.output_folder if args.output_folder else './output'

# Create output directory if it does not exist
try:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
except Exception as e:
    logging.info(f"Error creating directory: {e}")

# Assuming data is defined elsewhere
# Output JSON
try:
    with open(f'{output_folder}/output.json', 'w') as f:
        json.dump(data, f, cls=CustomEncoder)
except Exception as e:
    logging.info(f"Error writing to JSON file: {e}")

# Output to excel is requested
if args.output_xlsx:
    # Load your JSON data
    try:
        with open(f'{output_folder}/output.json') as f:
            data = json.load(f)
    except Exception as e:
        logging.info(f"Error reading from JSON file: {e}")
    
    # Assuming output_to_excel is defined elsewhere
    # Write xlsx file
    try:
        output_to_excel(data, output_folder)
    except Exception as e:
        logging.info(f"Error writing to Excel file: {e}")