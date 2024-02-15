from azure.mgmt.logic import LogicManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_logic_app(resource, rg, logic_client, root_element, resource_node_ids):
    # Get the Logic App
    logic_app = logic_client.workflows.get(rg.name, resource.name)
    
    print(f"Added Logic App {logic_app.name}")
    logic_app_id = f"{logic_app.name}_{uuid.uuid4()}"
    resource_node_ids[logic_app_id] = logic_app_id  # Use the Logic App name as the key
    logic_app_node = SubElement(root_element, 'mxCell', {'id': logic_app_id, 'value': logic_app.name, 'vertex': '1', 'parent': '1'})
    logic_app_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
