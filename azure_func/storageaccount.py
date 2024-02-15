from azure.mgmt.storage import StorageManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_storage_account(resource, rg, storage_client, root_element, resource_node_ids):
    # Get the storage account
    storage_account = storage_client.storage_accounts.get_properties(rg.name, resource.name)
    
    print(f"Added Storage Account {storage_account.name}")
    storage_account_id = f"{storage_account.name}_{uuid.uuid4()}"
    resource_node_ids[storage_account_id] = storage_account_id  # Use the storage account name as the key
    storage_account_node = SubElement(root_element, 'mxCell', {'id': storage_account_id, 'value': storage_account.name, 'vertex': '1', 'parent': '1'})
    storage_account_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids