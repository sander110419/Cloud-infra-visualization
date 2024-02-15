from azure.mgmt.datafactory import DataFactoryManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_data_factory(resource, rg, data_factory_client, root_element, resource_node_ids):
    # Get the Data Factory
    data_factory = data_factory_client.factories.get(rg.name, resource.name)
    
    print(f"Added Data Factory {data_factory.name}")
    data_factory_id = f"{data_factory.name}_{uuid.uuid4()}"
    resource_node_ids[data_factory_id] = data_factory_id  # Use the Data Factory name as the key
    data_factory_node = SubElement(root_element, 'mxCell', {'id': data_factory_id, 'value': data_factory.name, 'vertex': '1', 'parent': '1'})
    data_factory_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
