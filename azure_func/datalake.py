from azure.mgmt.datalake.store import DataLakeStoreAccountManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_data_lake_store(resource, rg, datalake_store_client, root_element, resource_node_ids):
    # Get the Data Lake Store
    data_lake_store = datalake_store_client.account.get(rg.name, resource.name)
    
    print(f"Added Data Lake Store {data_lake_store.name}")
    data_lake_store_id = f"{data_lake_store.name}_{uuid.uuid4()}"
    resource_node_ids[data_lake_store_id] = data_lake_store_id  # Use the Data Lake Store name as the key
    data_lake_store_node = SubElement(root_element, 'mxCell', {'id': data_lake_store_id, 'value': data_lake_store.name, 'vertex': '1', 'parent': '1'})
    data_lake_store_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
