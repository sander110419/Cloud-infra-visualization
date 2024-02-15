from azure.mgmt.sql import SqlManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_sql_server(resource, rg, sql_client, root_element, resource_node_ids):
    # Check if the server has already been added
    if resource.name in resource_node_ids:
        print(f"Server {resource.name} already exists.")
        return root_element, resource_node_ids

    server = sql_client.servers.get(rg.name, resource.name)
    print(f"Added SQL Server {server.name}")
    server_id = f"{server.name}_{uuid.uuid4()}"
    resource_node_ids[server.name] = server_id
    server_node = SubElement(root_element, 'mxCell', {'id': server_id, 'value': server.name, 'vertex': '1', 'parent': '1'})
    server_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
