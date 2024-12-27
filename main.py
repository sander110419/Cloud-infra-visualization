import json
import time
import os
import sys
import logging
from output_xlsx import output_to_excel
from functions import set_up_logging, parse_arguments, initialize_data, authenticate_to_azure, get_subscriptions, CustomEncoder
from azure_func import azure_imports
from datetime import timedelta
import subprocess
from azure_func.resource_functions import *
from json2docx import generate_word_document
from azure_func.resource_functions import handle_advisor_recommendations
from json2mermaid import generate_mermaid_flowchart, generate_html
import shutil


#parse arguments
args = parse_arguments()
#set up logging
set_up_logging(args.log_level)
#initialise data
data, start_time = initialize_data()
#authenticate to Azure
credential, subscription_client = authenticate_to_azure(args.tenant_id, args.client_id, args.client_secret, args.certificate_path, args.use_device_code, args.interactive_login)
#Get all subscriptions from erguments
subscriptions = get_subscriptions(subscription_client, args.subscription_id)

def get_client_classes():
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
        'recovery_backup_items': azure_imports.RecoveryServicesBackupClient,
        'advisor': azure_imports.AdvisorManagementClient
    }
    return client_classes

def get_resource_handlers():
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
        'Microsoft.Web/sites': [
            (handle_appservices, 'web'),
            (handle_function_app, 'web')
        ],
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
        'Microsoft.ServiceBus/namespaces' : [
            (handle_service_bus_namespaces, 'servicebus'),
            (handle_service_bus_queues, 'servicebus'),
            (handle_service_bus_topics, 'servicebus')
        ],
        'Microsoft.Authorization/locks' : [(handle_management_locks, 'lock')],
        'Microsoft.ContainerInstance/containerGroups' : [(handle_container_instance, 'container_instance')],
        'Microsoft.Network/loadBalancers' : [(handle_load_balancer, 'network')],
        'Microsoft.DataFactory/factories' : [(handle_data_factory, 'data_factory')],
        'Microsoft.Compute/galleries' : [
            (handle_image_galleries, 'compute'),
            (handle_galleries_images, 'compute'),
            (handle_galleries_images_versions, 'compute')

        ],
        'Microsoft.Compute/images' : [(handle_vm_images, 'compute')],
        'Microsoft.Compute/snapshots' : [(handle_vm_snapshot, 'compute')],
        'Microsoft.Network/publicIPAddresses' : [(handle_public_ip, 'network')],
        'Microsoft.Web/certificates' : [(handle_web_certificate, 'web')],
        'Microsoft.Web/connections' : [(handle_web_connections, 'web')],
        'Microsoft.StorageSync/storageSyncServices' : [(handle_storage_sync_services, 'storage_sync')],
        'Microsoft.Sql/managedInstances' : [
            (handle_sql_managed_instances, 'sql'),
            (handle_sql_managed_instances_db, 'sql')
        ],
        'Microsoft.Network/privateLinkServices' : [(handle_private_link_services, 'network')],
        'Microsoft.Logic/integrationAccounts' : [(handle_integration_accounts, 'logic')],
        'Microsoft.Communication/CommunicationServices' : [(handle_communication_services, 'communication')],
        'Microsoft.Sql/virtualCluster' : [(handle_virtual_cluster, 'sql')],
        'Microsoft.Compute/restorePointCollections' : [(handle_restore_point_collections, 'compute')],
        'Microsoft.Network/serviceEndpointPolicies' : [(handle_service_endpoint_policy, 'network')],
        'Microsoft.Insights/metricalerts' : [(handle_insights_metric_alerts, 'monitor')],
        'Microsoft.Insights/scheduledqueryrules' : [(handle_insights_scheduled_query_rules, 'monitor')],
        'Microsoft.Network/applicationGatewayWebApplicationFirewallPolicies' : [(handle_application_gateway_waf_policies, 'network')],
        'Microsoft.Cdn/profiles/afdendpoints' : [
            (handle_frontdoor_cdn, 'cdn'),
            (handle_afd_endpoints, 'cdn')
        ],
        'Microsoft.Network/routeTables' : [(handle_route_tables, 'network')],
        'microsoft.alertsmanagement/smartDetectorAlertRules' : [(handle_smart_detector_alert_rules, 'alertsmanagement')],
        'Microsoft.AlertsManagement/actionRules' : [(handle_action_rules, 'alertsmanagement')]
    }
    return resource_handlers

def process_subscription(subscription, data, args, client_classes):
    resource_client = azure_imports.ResourceManagementClient(credential, subscription)
    try:
        # Initialize an empty dictionary for this subscription
        data['Objects'][subscription] = {}

        # Initialize clients
        clients = {name: cls(credential, subscription) for name, cls in client_classes.items()}

        resource_handlers = get_resource_handlers()

        # Get specific resource group
        if args.resource_group:
            if args.subscription_id:
                try:
                    resource_groups = [resource_client.resource_groups.get(args.resource_group)]
                except Exception as e:
                    print(f"Resource group '{args.resource_group}' not found for subscription ID '{args.subscription_id}'")
                    return
            else:
                try:
                    resource_groups = [resource_client.resource_groups.get(args.resource_group)]
                except Exception as e:
                    print(f"Resource group '{args.resource_group}' not found")
                    return
        else:
            # Get all resource groups
            resource_groups = list(resource_client.resource_groups.list())

        # Filter resource groups by tag if tag_key and tag_value are provided
        if args.rgtag_key and args.rgtag_value:
            resource_groups = [rg for rg in resource_groups if rg.tags.get(args.rgtag_key) == args.rgtag_value]
        
        logging.info(f"Found {len(resource_groups)} resource groups")
        processing_times = []
        total_resourcegroups = len(resource_groups)
        for rg in resource_groups:
            process_resource_group(rg, resource_client, data, subscription, clients, resource_handlers, args, processing_times, total_resourcegroups)

    except Exception as e:
        logging.info(f"An error occurred: {e}")

def process_resource_group(rg, resource_client, data, subscription, clients, resource_handlers, args, processing_times, total_resourcegroups):
    # Filter resources by tag if rtag_key and rtag_value are provided
    if args.rtag_key and args.rtag_value:
        tag_filter = f"tagName eq '{args.rtag_key}' and tagValue eq '{args.rtag_value}'"
        # Get all resources with filter
        resources = list(resource_client.resources.list_by_resource_group(rg.name, tag_filter))

    else:
        # Get all resources within the resource group
        resources = list(resource_client.resources.list_by_resource_group(rg.name))

    total_resources = len(resources)
    start_time_resource = time.time()
    logging.info(f"Found {len(resources)} resources in resource group {rg.name}")

    # Initialize an empty list for this resource group
    data['Objects'][subscription][rg.name] = []

    # Add each resource to the diagram
    for resource in resources:
        process_resource(resource, rg, clients, resource_handlers, data, subscription, start_time_resource, processing_times, total_resources, total_resourcegroups)

def process_resource(resource, rg, clients, resource_handlers, data, subscription, start_time_resource, processing_times, total_resources, total_resourcegroups):
    total_resources -= 1
    elapsed_time_resource = time.time() - start_time_resource
    processing_times.append(elapsed_time_resource)
    #logging.info(resource.type)

       # Get the handler functions for this resource type
    logging.info(f"Processing resource {resource.name} of type {resource.type}")
    handler_infos = resource_handlers.get(resource.type)
    resource_data = {}
    if handler_infos is not None:
        for handler_info in handler_infos:
            handler, client_key = handler_info
            client = clients[client_key]
            # Call the handler function and get the data
            resource_details = handler(resource, rg, client)
            if 'Error' in resource_details:
                logging.warning(f"Error in {handler.__name__}: {resource_details['Error']}")
            else:
                logging.info(f"Finished calling {handler.__name__} for resource {resource.name}")
            resource_data['ResourceType'] = resource.type
            resource_data['Details'] = resource_details
    else:
        # If no specific handler, just store the basic resource information
        resource_data['ResourceType'] = resource.type
        resource_data['Details'] = resource.as_dict()

    # Fetch Azure Advisor recommendations
    advisor_client = clients['advisor']
    recommendations = handle_advisor_recommendations(resource.id, advisor_client)
    resource_data['Recommendations'] = recommendations

    data['Objects'][subscription][rg.name].append(resource_data)

    # Update progress bar
    update_progress_bar(total_resources, rg, total_resourcegroups, processing_times)

def update_progress_bar(total_resources, rg, total_resourcegroups, processing_times):
    average_time = sum(processing_times) / len(processing_times)
    estimated_remaining = ((average_time * total_resources) / 3) * total_resourcegroups
    estimated_remaining_td = timedelta(seconds=int(estimated_remaining))
    if sys.stdout.isatty():
        # We are running in a real terminal
        print(f"\r{total_resources} resources left to process in RG {rg.name}, {total_resourcegroups} RG's left. Estimated time remaining: {str(estimated_remaining_td)}", end="")
    else:
        # We are being piped or redirected
        print(f"{total_resources} resources left to process in RG {rg.name}, {total_resourcegroups} RG's left. Estimated time remaining: {str(estimated_remaining_td)}")
    total_resourcegroups -= 1

def authenticate(args):
    client_secret = None if args.use_device_code or args.certificate_path or args.interactive_login else args.client_secret
    certificate_path = None if args.use_device_code else args.certificate_path
    _, subscription_client = authenticate_to_azure(args.tenant_id, args.client_id, client_secret, certificate_path, args.use_device_code, args.interactive_login)
    return subscription_client

def create_directory(output_folder):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    except Exception as e:
        logging.error(f"Error creating directory: {e}")

def write_json(data, output_folder, output_json_file):
    try:
        with open(os.path.join(output_folder, output_json_file), 'w') as f:
            json.dump(data, f, cls=CustomEncoder)
    except Exception as e:
        logging.error(f"Error writing to JSON file: {e}")

def read_json(output_folder, output_json_file):
    try:
        with open(os.path.join(output_folder, output_json_file)) as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Error reading from JSON file: {e}")
    return data

def write_excel(data, output_folder):
    try:
        output_to_excel(data, output_folder)
    except Exception as e:
        logging.error(f"Error writing to Excel file: {e}")

def write_drawio(output_folder, output_json_file):
    try:
        subprocess.call(['python', os.path.join('.', 'azure_func', 'json2xml.py'), os.path.join(output_folder, output_json_file), os.path.join(output_folder, 'output.drawio')])
    except Exception as e:
        logging.error(f"Error writing to DrawIO file: {e}")

def generate_output():
    #parse arguments
    args = parse_arguments()
    #set up logging
    set_up_logging(args.log_level)
    #initialise data
    data, start_time = initialize_data()
    #authenticate to Azure
    subscription_client = authenticate(args)

    #Get all subscriptions from erguments
    subscriptions = get_subscriptions(subscription_client, args.subscription_id)

    client_classes = get_client_classes()

    for subscription in subscriptions:
        process_subscription(subscription, data, args, client_classes)

    #record endtime for json properties
    end_time = time.time()
    duration = end_time - start_time

    data['Properties']['Duration'] = duration

    # Get output folder from arguments
    output_folder = args.output_folder if args.output_folder else os.path.join('.', 'output')
    output_json_file = 'output.json'
    # Create output directory if it does not exist
    create_directory(output_folder)

    # Output JSON
    write_json(data, output_folder, output_json_file)

    # Output to excel is requested
    if args.output_xlsx:
        # Load your JSON data
        data = read_json(output_folder, output_json_file)
        
        # Write xlsx file
        write_excel(data, output_folder)

    # Output to drawio is requested
    if args.output_drawio:
        write_drawio(output_folder, output_json_file)

    # Output to dockx is requested
    if args.output_docx:
        data = read_json(output_folder, output_json_file)  # Read the JSON data
        generate_word_document(data, output_folder)  # Generate the Word document

    if args.output_html:
        mermaid_code = generate_mermaid_flowchart(data)
        html_content = generate_html(mermaid_code)
        
        # Write the HTML file
        with open(os.path.join(output_folder, 'output.html'), 'w') as f:
            f.write(html_content)
        
        # Copy icons folder to output location
        icons_source = os.path.join(os.path.dirname(__file__), 'icons')
        icons_destination = os.path.join(output_folder, 'icons')
        
        if os.path.exists(icons_source):
            if os.path.exists(icons_destination):
                shutil.rmtree(icons_destination)
            shutil.copytree(icons_source, icons_destination)

if __name__ == "__main__":
    generate_output()