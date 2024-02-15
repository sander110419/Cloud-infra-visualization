from azure.mgmt.servicebus import ServiceBusManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_service_bus(resource, rg, servicebus_client, root_element, resource_node_ids):
    # Get the Service Bus
    service_bus = servicebus_client.namespaces.get(rg.name, resource.name)
    
    print(f"Added Service Bus {service_bus.name}")
    service_bus_id = f"{service_bus.name}_{uuid.uuid4()}"
    resource_node_ids[service_bus_id] = service_bus_id  # Use the Service Bus name as the key
    service_bus_node = SubElement(root_element, 'mxCell', {'id': service_bus_id, 'value': service_bus.name, 'vertex': '1', 'parent': '1'})
    service_bus_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids