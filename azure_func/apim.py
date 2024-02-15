from azure.mgmt.apimanagement import ApiManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_api_management(resource, rg, apim_client, root_element, resource_node_ids):
    # Get the API Management
    api_management = apim_client.api_management_service.get(rg.name, resource.name)
    
    print(f"Added API Management {api_management.name}")
    api_management_id = f"{api_management.name}_{uuid.uuid4()}"
    resource_node_ids[api_management_id] = api_management_id  # Use the API Management name as the key
    api_management_node = SubElement(root_element, 'mxCell', {'id': api_management_id, 'value': api_management.name, 'vertex': '1', 'parent': '1'})
    api_management_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
