from azure.mgmt.sql import SqlManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_sql_db(resource, rg, sql_client, root_element, resource_node_ids):
    # Split the resource name into server name and database name
    server_name, database_name = resource.name.split('/')
    
    # Get the database
    db = sql_client.databases.get(rg.name, server_name, database_name)
    
    print(f"Added SQL DB {db.name}")
    db_id = f"{server_name}/{db.name}_{uuid.uuid4()}"
    resource_node_ids[db_id] = db_id  # Use the combined server and database name as the key
    db_node = SubElement(root_element, 'mxCell', {'id': db_id, 'value': db.name, 'vertex': '1', 'parent': '1'})
    db_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids