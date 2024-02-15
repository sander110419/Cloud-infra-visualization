import uuid
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.mgmt.storage import StorageManagementClient


from lxml.etree import Element, SubElement, tostring
from azure_func.auth import authenticate
from azure_func.vm import handle_virtual_machine
from azure_func.nic import handle_network_interface
from azure_func.sql import handle_sql_server
from azure_func.sqldb import handle_sql_db
from azure_func.link import link_nics_to_vms, link_dbs_to_servers,link_disks_to_vms,link_app_services_to_app_service_plans
from azure_func.disk import handle_disk
from azure_func.appservice import handle_app_service
from azure_func.appserviceplan import handle_app_service_plan
from azure_func.keyvault import handle_key_vault
from azure_func.loganalytics import handle_log_analytics_workspace
from azure_func.storageaccount import handle_storage_account


# Authenticate to Azure
tenant_id = ""
client_id = ""
client_secret = ""

credential = authenticate(tenant_id, client_id, client_secret)

subscription_client = SubscriptionClient(credential)

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
        resource_client = ResourceManagementClient(credential, subscription)
        network_client = NetworkManagementClient(credential, subscription)
        compute_client = ComputeManagementClient(credential, subscription)
        sql_client = SqlManagementClient(credential, subscription)
        web_client = WebSiteManagementClient(credential, subscription)
        kv_client = KeyVaultManagementClient(credential, subscription)
        la_client = LogAnalyticsManagementClient(credential, subscription)
        storage_client = StorageManagementClient(credential, subscription)


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
                    root_element, resource_node_ids = handle_network_interface(resource, rg, network_client, root_element, resource_node_ids)

                elif resource.type == "Microsoft.Compute/virtualMachines":
                    root_element, resource_node_ids = handle_virtual_machine(resource, rg, compute_client, root_element, resource_node_ids)

                elif resource.type == "Microsoft.Sql/servers":
                    root_element, resource_node_ids = handle_sql_server(resource, rg, sql_client, root_element, resource_node_ids)
                
                elif resource.type == "Microsoft.Sql/servers/databases":
                    root_element, resource_node_ids = handle_sql_db(resource, rg, sql_client, root_element, resource_node_ids)

                elif resource.type == "Microsoft.Compute/disks":
                    root_element, resource_node_ids = handle_disk(resource, rg, compute_client, root_element, resource_node_ids)

                elif resource.type == "Microsoft.Web/sites":
                    root_element, resource_node_ids = handle_app_service(resource, rg, web_client, root_element, resource_node_ids)

                elif resource.type == "Microsoft.Web/serverfarms":
                    root_element, resource_node_ids = handle_app_service_plan(resource, rg, web_client, root_element, resource_node_ids)

                elif resource.type == 'Microsoft.KeyVault/vaults':
                    root_element, resource_node_ids = handle_key_vault(resource, rg, kv_client, root_element, resource_node_ids)
                
                elif resource.type == 'Microsoft.OperationalInsights/workspaces':
                    root_element, resource_node_ids = handle_log_analytics_workspace(resource, rg, la_client, root_element, resource_node_ids)

                elif resource.type == 'Microsoft.Storage/storageAccounts':
                    root_element, resource_node_ids = handle_storage_account(resource, rg, storage_client, root_element, resource_node_ids)

        #link resources that can be linked
        root_element = link_nics_to_vms(compute_client, network_client, resource_groups, root_element, resource_node_ids)
        root_element = link_dbs_to_servers(sql_client, resource_groups, root_element, resource_node_ids)
        root_element = link_disks_to_vms(compute_client, resource_groups, root_element, resource_node_ids)
        root_element = link_app_services_to_app_service_plans(web_client, resource_groups, root_element, resource_node_ids)


    except Exception as e:
        print(f"An error occurred: {e}")

# Write XML to file
xml_str = tostring(mxfile, pretty_print=True).decode()
with open('azure_resources.xml', 'w') as f:
    f.write(xml_str)