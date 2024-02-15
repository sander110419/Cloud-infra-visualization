from azure.mgmt.eventhub import EventHubManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_event_hub(resource, rg, eventhub_client, root_element, resource_node_ids):
    # Get the Event Hub
    event_hub = eventhub_client.event_hubs.get(rg.name, resource.name)
    
    print(f"Added Event Hub {event_hub.name}")
    event_hub_id = f"{event_hub.name}_{uuid.uuid4()}"
    resource_node_ids[event_hub_id] = event_hub_id  # Use the Event Hub name as the key
    event_hub_node = SubElement(root_element, 'mxCell', {'id': event_hub_id, 'value': event_hub.name, 'vertex': '1', 'parent': '1'})
    event_hub_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
