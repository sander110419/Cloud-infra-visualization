from azure.mgmt.eventgrid import EventGridManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_event_grid(resource, rg, event_grid_client, root_element, resource_node_ids):
    # Get the Logic App
    event_grid = event_grid_client.workflows.get(rg.name, resource.name)
    
    print(f"Added Logic App {event_grid.name}")
    event_grid_id = f"{event_grid.name}_{uuid.uuid4()}"
    resource_node_ids[event_grid_id] = event_grid_id  # Use the Logic App name as the key
    event_grid_node = SubElement(root_element, 'mxCell', {'id': event_grid_id, 'value': event_grid.name, 'vertex': '1', 'parent': '1'})
    event_grid_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
