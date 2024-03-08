import json
import time
from output_xlsx import output_to_excel
from functions import parse_arguments, initialize_data, authenticate_to_azure, get_subscriptions, CustomEncoder
from azure_func import azure_imports

#parse arguments
args = parse_arguments()
#initialise data
data, start_time = initialize_data()
#authenticate to Azure
credential, subscription_client = authenticate_to_azure(args.tenant_id, args.client_id, args.client_secret)
#Get all subscriptions from erguments
subscriptions = get_subscriptions(subscription_client, args.subscription_id)

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
        container_client = azure_imports.ContainerInstanceManagementClient(credential, subscription)
        eventhub_client = azure_imports.EventHubManagementClient(credential, subscription)
        logic_client = azure_imports.LogicManagementClient(credential, subscription)
        container_registry_client = azure_imports.ContainerRegistryManagementClient(credential, subscription)
        lock_client  = azure_imports.ManagementLockClient(credential, subscription)
        servicebus_client = azure_imports.ServiceBusManagementClient(credential, subscription)
        container_instance_client = azure_imports.ContainerInstanceManagementClient(credential, subscription)
        storage_sync_client = azure_imports.MicrosoftStorageSync(credential, subscription)
        communication_client = azure_imports.CommunicationServiceManagementClient(credential, subscription)
        resource_handlers = {
            'Microsoft.Network/networkInterfaces': (azure_imports.handle_network_interface, network_client),
            'Microsoft.Compute/virtualMachines': (azure_imports.handle_virtual_machine, compute_client),
            'Microsoft.Compute/virtualMachineScaleSets': (azure_imports.handle_vm_scale_set, compute_client),
            'Microsoft.Sql/servers': (azure_imports.handle_sql_server, sql_client),
            'Microsoft.Sql/servers/databases': (azure_imports.handle_sql_db, sql_client),
            'Microsoft.Compute/disks': (azure_imports.handle_disk, compute_client),
            'Microsoft.Web/serverFarms': (azure_imports.handle_app_service_plan, web_client),
            'Microsoft.Web/sites': (azure_imports.handle_appservices, web_client),
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
            'Microsoft.Network/privateDnsZones': (azure_imports.handle_private_dns_zones, network_client),
            'Microsoft.Cdn/profiles': (azure_imports.handle_cdn_profile, cdn_client),
            'Microsoft.ServiceFabric/clusters': (azure_imports.handle_service_fabric_cluster, sf_client),
            'Microsoft.DevTestLab/schedules': (azure_imports.handle_devtest_lab, devtest_client),
            'Microsoft.Insights/actionGroups' : (azure_imports.handle_monitor_action_group, monitor_client),
            'Microsoft.Scheduler/jobCollections': (azure_imports.handle_scheduler_job_collection, scheduler_client),
            'Microsoft.DocumentDb/databaseAccounts' : (azure_imports.handle_cosmosdb_account, cosmosdb_client),
            'Microsoft.EventGrid/eventSubscriptions': (azure_imports.handle_event_grid_subscriptions, event_grid_client),
            'Microsoft.EventGrid/topics': (azure_imports.handle_event_grids, event_grid_client),
            'Microsoft.RecoveryServices/vaults': (azure_imports.handle_recovery_services_vault, recovery_services_client),
            'Microsoft.Network/virtualNetworks': (azure_imports.handle_vnet, network_client),
            'Microsoft.Network/virtualNetworks/subnets': (azure_imports.handle_all_subnets, network_client),
            'Microsoft.Network/privateEndpoints': (azure_imports.handle_private_endpoint, network_client),
            #'Microsoft.Compute/proximityPlacementGroups': (azure_imports.handle_proximity_placement_group, network_client),
            'Microsoft.Network/networkSecurityGroups': (azure_imports.handle_network_security_group, network_client),
            'Microsoft.App/containerApps': (azure_imports.handle_container_app, container_client),
            'Microsoft.EventHub/namespaces': (azure_imports.handle_event_hub, eventhub_client),
            'Microsoft.Logic/workflows': (azure_imports.handle_logic_app, logic_client),
            'Microsoft.ContainerRegistry/registries' : (azure_imports.handle_container_registry, container_registry_client),
            'Microsoft.ServiceBus/namespaces' : (azure_imports.handle_service_bus_queues, servicebus_client),
            'Microsoft.Authorization/locks' : (azure_imports.handle_management_locks, lock_client),
            'Microsoft.ContainerInstance/containerGroups' : (azure_imports.handle_container_instance, container_instance_client),
            'Microsoft.Network/loadBalancers' : (azure_imports.handle_load_balancer, network_client),
            'Microsoft.DataFactory/factories' : (azure_imports.handle_data_factory, data_factory_client),
            'Microsoft.Compute/galleries' : (azure_imports.handle_image_galleries, compute_client),
            'Microsoft.Compute/images' : (azure_imports.handle_vm_images, compute_client),
            'Microsoft.Compute/snapshots' : (azure_imports.handle_vm_snapshot, compute_client),
            'Microsoft.Network/publicIPAddresses' : (azure_imports.handle_public_ip, network_client),
            'Microsoft.Web/certificates' : (azure_imports.handle_web_certificate, web_client),
            'Microsoft.Web/connections' : (azure_imports.handle_web_connections, web_client),
            'Microsoft.StorageSync/storageSyncServices' : (azure_imports.handle_storage_sync_services, storage_sync_client),
            'Microsoft.Sql/managedInstances' : (azure_imports.handle_sql_managed_instances, sql_client),
            'Microsoft.Network/privateLinkServices' : (azure_imports.handle_private_link_services, network_client),
            'Microsoft.Logic/integrationAccounts' : (azure_imports.handle_integration_accounts, logic_client),
            'Microsoft.Communication/CommunicationServices' : (azure_imports.handle_communication_services, communication_client),
            'Microsoft.Sql/virtualCluster' : (azure_imports.handle_virtual_cluster, sql_client),
            'Microsoft.Compute/restorePointCollections' : (azure_imports.handle_restore_point_collections, compute_client),
            'Microsoft.Compute/virtualMachines/extensions' : (azure_imports.handle_vm_extensions, compute_client),
            'Microsoft.Sql/managedInstances/databases' : (azure_imports.handle_sql_managed_instances_db, sql_client),
            #'Microsoft.DataMigration/SqlMigrationServices' : (azure_imports.handle_sql_migration_services, datamigration_client),
            'Microsoft.Network/serviceEndpointPolicies' : (azure_imports.handle_service_endpoint_policy, network_client),
            'Microsoft.Insights/components' : (azure_imports.handle_insights_components, monitor_client),
            'Microsoft.Insights/metricalerts' : (azure_imports.handle_insights_metric_alerts, monitor_client),
            'Microsoft.Insights/scheduledqueryrules' : (azure_imports.handle_insights_scheduled_query_rules, monitor_client),
            'Microsoft.Network/applicationGatewayWebApplicationFirewallPolicies' : (azure_imports.handle_application_gateway_waf_policies, network_client),
            'Microsoft.Cdn/profiles/afdendpoints' : (azure_imports.handle_afd_endpoints, cdn_client),
            'Microsoft.Network/routeTables' : (azure_imports.handle_route_tables, network_client),
            'Microsoft.Compute/galleries/images/versions' : (azure_imports.handle_galleries_images_versions, compute_client),
            'Microsoft.Compute/galleries/images' : (azure_imports.handle_galleries_images, compute_client)
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
                print(resource.type)

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

#record endtime for json properties
end_time = time.time()
duration = end_time - start_time

data['Properties']['Duration'] = duration

#Output JSON
with open('output.json', 'w') as f:
    json.dump(data, f, cls=CustomEncoder)

#Output to excel is requested
if args.output_xlsx:
    with open('output.json', 'w') as f:
        json.dump(data, f, cls=CustomEncoder)

    # Load your JSON data
    with open('output.json') as f:
        data = json.load(f)

    output_to_excel(data)