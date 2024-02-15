from azure.mgmt.network import NetworkManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_virtual_network(resource, rg, network_client, root_element, resource_node_ids):
    # Get the Virtual Network
    virtual_network = network_client.virtual_networks.get(rg.name, resource.name)
    
    print(f"Added Virtual Network {virtual_network.name}")
    virtual_network_id = f"{virtual_network.name}_{uuid.uuid4()}"
    resource_node_ids[virtual_network_id] = virtual_network_id  # Use the Virtual Network name as the key
    virtual_network_node = SubElement(root_element, 'mxCell', {'id': virtual_network_id, 'value': virtual_network.name, 'vertex': '1', 'parent': '1'})
    virtual_network_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids