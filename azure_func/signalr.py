from azure.mgmt.signalr import SignalRManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_signalr_service(resource, rg, signalr_client, root_element, resource_node_ids):
    # Get the SignalR Service
    signalr_service = signalr_client.signal_r.get(rg.name, resource.name)
    
    print(f"Added SignalR Service {signalr_service.name}")
    signalr_service_id = f"{signalr_service.name}_{uuid.uuid4()}"
    resource_node_ids[signalr_service_id] = signalr_service_id  # Use the SignalR Service name as the key
    signalr_service_node = SubElement(root_element, 'mxCell', {'id': signalr_service_id, 'value': signalr_service.name, 'vertex': '1', 'parent': '1'})
    signalr_service_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
