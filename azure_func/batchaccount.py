from azure.mgmt.batch import BatchManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_batch_account(resource, rg, batch_client, root_element, resource_node_ids):
    # Get the Batch Account
    batch_account = batch_client.batch_account.get(rg.name, resource.name)
    
    print(f"Added Batch Account {batch_account.name}")
    batch_account_id = f"{batch_account.name}_{uuid.uuid4()}"
    resource_node_ids[batch_account_id] = batch_account_id  # Use the Batch Account name as the key
    batch_account_node = SubElement(root_element, 'mxCell', {'id': batch_account_id, 'value': batch_account.name, 'vertex': '1', 'parent': '1'})
    batch_account_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
