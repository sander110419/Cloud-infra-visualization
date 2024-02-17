from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_cognitive_service(resource, rg, cognitive_client, root_element, resource_node_ids):
    cognitive_service = cognitive_client.accounts.get(rg.name, resource.name)
    print(f"Added Cognitive Service {cognitive_service.name}")
    cognitive_id = f"{cognitive_service.name}_{uuid.uuid4()}"
    resource_node_ids[cognitive_service.name] = cognitive_id
    cognitive_node = SubElement(root_element, 'mxCell', {'id': cognitive_id, 'value': cognitive_service.name, 'vertex': '1', 'parent': '1'})
    cognitive_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids