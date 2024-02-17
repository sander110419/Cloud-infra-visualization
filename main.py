import uuid
import azure_func.azure_imports as azure_imports
from lxml.etree import Element, SubElement, tostring

# Authenticate to Azure
tenant_id = ""
client_id = ""
client_secret = ""

credential = azure_imports.authenticate(tenant_id, client_id, client_secret)

subscription_client = azure_imports.SubscriptionClient(credential)

subscriptions = ["bf7c8d7a-ed8c-49d6-864d-8902cdbe1a97"]

# Create root element for draw.io compatible XML
mxfile = Element('mxfile')
diagram = SubElement(mxfile, 'diagram', {'id': '6hGFLwfOUW9BJ-s0fimq', 'name': 'Page-1'})
root = SubElement(diagram, 'mxGraphModel', {'dx': '846', 'dy': '467', 'grid': '1', 'gridSize': '10', 'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1', 'fold': '1', 'page': '1', 'pageScale': '1', 'pageWidth': '827', 'pageHeight': '1169'})

root_element = SubElement(root, 'root')

# Add the root and default parent cells
SubElement(root_element, 'mxCell', {'id': '0'})
SubElement(root_element, 'mxCell', {'id': '1', 'parent': '0'})

# Dictionary to store resource node IDs
resource_node_ids = {}

for subscription in subscriptions:
    try:
        resource_client = azure_imports.ResourceManagementClient(credential, subscription)
        network_client = azure_imports.NetworkManagementClient(credential, subscription)
        compute_client = azure_imports.ComputeManagementClient(credential, subscription)
        sql_client = azure_imports.SqlManagementClient(credential, subscription)
        web_client = azure_imports.WebSiteManagementClient(credential, subscription)
        kv_client = azure_imports.KeyVaultManagementClient(credential, subscription)
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


        # Step 3: Get all resource groups
        resource_groups = list(resource_client.resource_groups.list())

        print(f"Found {len(resource_groups)} resource groups")

        for rg in resource_groups:
            # Add each resource group as a node, added UUID because they are not always unique
            node_id = f"{rg.name}_{uuid.uuid4()}"
            node = SubElement(root_element, 'mxCell', {'id': node_id, 'value': rg.name, 'vertex': '1', 'parent': '1'})
            node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))

            # Get resources within the resource group
            resources = list(resource_client.resources.list_by_resource_group(rg.name))

            print(f"Found {len(resources)} resources in resource group {rg.name}")

            # Add each resource to the diagram
            for resource in resources:
                res_node_id = f"{resource.name}_{uuid.uuid4()}"
                resource_node_ids[resource.name] = res_node_id
                res_node = SubElement(root_element, 'mxCell', {'id': res_node_id, 'value': resource.name, 'vertex': '1', 'parent': '1'})
                res_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
                edge = SubElement(root_element, 'mxCell', {'id': f'{node_id}-{res_node_id}', 'value': '', 'edge': '1', 'source': node_id, 'target': res_node_id, 'parent': '1'})
                edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

                if resource.type == "Microsoft.Network/networkInterfaces":
                    root_element, resource_node_ids = azure_imports.handle_network_interface(resource, rg, network_client, root_element, resource_node_ids)
                elif resource.type == "Microsoft.Compute/virtualMachines":
                    root_element, resource_node_ids = azure_imports.handle_virtual_machine(resource, rg, compute_client, root_element, resource_node_ids)
                elif resource.type == "Microsoft.Sql/servers":
                    root_element, resource_node_ids = azure_imports.handle_sql_server(resource, rg, sql_client, root_element, resource_node_ids)
                elif resource.type == "Microsoft.Sql/servers/databases":
                    root_element, resource_node_ids = azure_imports.handle_sql_db(resource, rg, sql_client, root_element, resource_node_ids)
                elif resource.type == "Microsoft.Compute/disks":
                    root_element, resource_node_ids = azure_imports.handle_disk(resource, rg, compute_client, root_element, resource_node_ids)
                elif resource.type == "Microsoft.Web/sites":
                    root_element, resource_node_ids = azure_imports.handle_app_service(resource, rg, web_client, root_element, resource_node_ids)
                elif resource.type == "Microsoft.Web/serverfarms":
                    root_element, resource_node_ids = azure_imports.handle_app_service_plan(resource, rg, web_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.KeyVault/vaults':
                    root_element, resource_node_ids = azure_imports.handle_key_vault(resource, rg, kv_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.OperationalInsights/workspaces':
                    root_element, resource_node_ids = azure_imports.handle_log_analytics_workspace(resource, rg, la_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Storage/storageAccounts':
                    root_element, resource_node_ids = azure_imports.handle_storage_account(resource, rg, storage_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.ApiManagement/service':
                    root_element, resource_node_ids = azure_imports.handle_api_management(resource, rg, apim_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.DataLakeStore/accounts':
                    root_element, resource_node_ids = azure_imports.handle_data_lake_store(resource, rg, datalake_store_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.DataFactory/factories':
                    root_element, resource_node_ids = azure_imports.handle_data_factory(resource, rg, data_factory_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.StreamAnalytics/streamingjobs':
                    root_element, resource_node_ids = azure_imports.handle_stream_analytics_job(resource, rg, stream_analytics_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.ContainerService/managedClusters':
                    root_element, resource_node_ids = azure_imports.handle_aks_service(resource, rg, kubernetes_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Search/searchServices':
                    root_element, resource_node_ids = azure_imports.handle_search_service(resource, rg, search_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.SignalRService/SignalR':
                    root_element, resource_node_ids = azure_imports.handle_signalr_service(resource, rg, signalr_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.BotService/botServices':
                    root_element, resource_node_ids = azure_imports.handle_bot_service(resource, rg, bot_service_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Devices/IotHubs':
                    root_element, resource_node_ids = azure_imports.handle_iot_hub(resource, rg, iot_hub_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.CognitiveServices/accounts':
                    root_element, resource_node_ids = azure_imports.handle_cognitive_service(resource, rg, cognitive_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Network/dnszones':
                    root_element, resource_node_ids = azure_imports.handle_dns_zone(resource, rg, dns_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Cdn/profiles':
                    root_element, resource_node_ids = azure_imports.handle_cdn_profile(resource, rg, cdn_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.ServiceFabric/clusters':
                    root_element, resource_node_ids = azure_imports.handle_service_fabric_cluster(resource, rg, sf_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.DevTestLab/schedules':
                    root_element, resource_node_ids = azure_imports.handle_devtest_lab(resource, rg, devtest_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Insights/actionGroups':
                    root_element, resource_node_ids = azure_imports.handle_monitor_action_group(resource, rg, monitor_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.Scheduler/jobCollections':
                    root_element, resource_node_ids = azure_imports.handle_scheduler_job_collection(resource, rg, scheduler_client, root_element, resource_node_ids)
                elif resource.type == 'Microsoft.DocumentDB/databaseAccounts':
                    root_element, resource_node_ids = azure_imports.handle_cosmosdb_account(resource, rg, cosmosdb_client, root_element, resource_node_ids)

        #link resources that can be linked
        root_element = azure_imports.link_nics_to_vms(compute_client, network_client, resource_groups, root_element, resource_node_ids)
        root_element = azure_imports.link_dbs_to_servers(sql_client, resource_groups, root_element, resource_node_ids)
        root_element = azure_imports.link_disks_to_vms(compute_client, resource_groups, root_element, resource_node_ids)
        root_element = azure_imports.link_app_services_to_app_service_plans(web_client, resource_groups, root_element, resource_node_ids)


    except Exception as e:
        print(f"An error occurred: {e}")

# Write XML to file
xml_str = tostring(mxfile, pretty_print=True).decode()
with open('azure_resources.xml', 'w') as f:
    f.write(xml_str)