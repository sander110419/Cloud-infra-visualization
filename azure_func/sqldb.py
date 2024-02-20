from azure.mgmt.sql import SqlManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_sql_db(resource, rg, sql_client, root_element, resource_node_ids):
    # Split the resource name into server name and database name
    server_name, database_name = resource.name.split('/')
    
    # Create a unique id for the database
    db_id = f"{server_name}/{database_name}"
    
    # Check if a DB node with the same id already exists
    if db_id in resource_node_ids:
        print(f"DB {db_id} already exists, skipping...")
        return root_element, resource_node_ids
    
    # Get the database
    db = sql_client.databases.get(rg.name, server_name, database_name)
    
    print(f"Added SQL DB {db.name}")
    
    # Add the new database id to the dictionary
    resource_node_ids[db_id] = db_id  
    
    # Create a new XML element for the database
    db_node = SubElement(root_element, 'mxCell', {'id': db_id, 'value': db.name, 'vertex': '1', 'parent': '1'})
    db_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    
    return root_element, resource_node_ids
