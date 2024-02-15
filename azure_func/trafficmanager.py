from azure.mgmt.trafficmanager import TrafficManagerManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_traffic_manager(resource, rg, traffic_manager_client, root_element, resource_node_ids):
    # Get the Traffic Manager
    traffic_manager = traffic_manager_client.profiles.get(rg.name, resource.name)
    
    print(f"Added Traffic Manager {traffic_manager.name}")
    traffic_manager_id = f"{traffic_manager.name}_{uuid.uuid4()}"
    resource_node_ids[traffic_manager_id] = traffic_manager_id  # Use the Traffic Manager name as the key
    traffic_manager_node = SubElement(root_element, 'mxCell', {'id': traffic_manager_id, 'value': traffic_manager.name, 'vertex': '1', 'parent': '1'})
    traffic_manager_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
