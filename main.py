import uuid
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.sql import SqlManagementClient
from lxml.etree import Element, SubElement, tostring

# Step 1: Authenticate to Azure
tenant_id = "<your-tenant-id>"
client_id = "<your-client-id>"
client_secret = "<your-client-secret>"

credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

subscription_client = SubscriptionClient(credential)

# Step 2: Get all subscriptions
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
                if resource.type != "Microsoft.Sql/servers":
                    res_node_id = f"{resource.name}_{uuid.uuid4()}"
                    resource_node_ids[resource.name] = res_node_id
                    res_node = SubElement(root_element, 'mxCell', {'id': res_node_id, 'value': resource.name, 'vertex': '1', 'parent': '1'})
                    res_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
                    edge = SubElement(root_element, 'mxCell', {'id': f'{node_id}-{res_node_id}', 'value': '', 'edge': '1', 'source': node_id, 'target': res_node_id, 'parent': '1'})
                    edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

                    # Link NICs to VMs if the resource is a VM
                    if resource.type == "Microsoft.Compute/virtualMachines":
                        nics = network_client.network_interfaces.list_all()
                        vm = compute_client.virtual_machines.get(rg.name, resource.name)

                        for nic in nics:
                            if vm.location == nic.location:
                                if vm.network_profile.network_interfaces[0].id == nic.id:
                                    print(f"Linked NIC {nic.name} to VM {vm.name}")
                                    if nic.name not in resource_node_ids:
                                        print(f"NIC {nic.name} not found in resource_node_ids. Adding it now.")
                                        nic_id = f"{nic.name}_{uuid.uuid4()}"
                                        resource_node_ids[nic.name] = nic_id
                                        nic_node = SubElement(root_element, 'mxCell', {'id': nic_id, 'value': nic.name, 'vertex': '1', 'parent': '1'})
                                        nic_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
                                    else:
                                        nic_id = resource_node_ids[nic.name]
                                    vm_id = resource_node_ids[vm.name]
                                    edge = SubElement(root_element, 'mxCell', {'id': f'{nic_id}-{vm_id}', 'value': '', 'edge': '1', 'source': nic_id, 'target': vm_id, 'parent': '1'})
                                    edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

            servers = sql_client.servers.list_by_resource_group(rg.name)
            for server in servers:
                # Create a node for the server
                server_node_id = f"{server.name}_{uuid.uuid4()}"
                resource_node_ids[server.name] = server_node_id
                server_node = SubElement(root_element, 'mxCell', {'id': server_node_id, 'value': server.name, 'vertex': '1', 'parent': '1'})
                server_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
                # Create an edge between the server and its resource group
                edge = SubElement(root_element, 'mxCell', {'id': f'{node_id}-{server_node_id}', 'value': '', 'edge': '1', 'source': node_id, 'target': server_node_id, 'parent': '1'})
                edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

                databases = sql_client.databases.list_by_server(rg.name, server.name)
                for db in databases:
                    # Create a node for the database
                    db_node_id = f"{db.name}_{uuid.uuid4()}"
                    resource_node_ids[db.name] = db_node_id
                    db_node = SubElement(root_element, 'mxCell', {'id': db_node_id, 'value': db.name, 'vertex': '1', 'parent': '1'})
                    db_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))

                    # Create an edge between the server and the database
                    edge = SubElement(root_element, 'mxCell', {'id': f'{server_node_id}-{db_node_id}', 'value': '', 'edge': '1', 'source': server_node_id, 'target': db_node_id, 'parent': '1'})
                    edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

    except Exception as e:
        print(f"An error occurred: {e}")

# Write XML to file
xml_str = tostring(mxfile, pretty_print=True).decode()
with open('test-output/azure_resources.xml', 'w') as f:
    f.write(xml_str)
