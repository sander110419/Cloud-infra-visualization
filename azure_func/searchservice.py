from azure.mgmt.search import SearchManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_search_service(resource, rg, search_client, root_element, resource_node_ids):
    # Get the Search Service
    search_service = search_client.services.get(rg.name, resource.name)
    
    print(f"Added Search Service {search_service.name}")
    search_service_id = f"{search_service.name}_{uuid.uuid4()}"
    resource_node_ids[search_service_id] = search_service_id  # Use the Search Service name as the key
    search_service_node = SubElement(root_element, 'mxCell', {'id': search_service_id, 'value': search_service.name, 'vertex': '1', 'parent': '1'})
    search_service_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
