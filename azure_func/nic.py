from azure.mgmt.network import NetworkManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_network_interface(resource, rg, network_client, root_element, resource_node_ids):
    # Check if a nic node with the same name already exists
    if resource.name in resource_node_ids:
        print(f"NIC {resource.name} already exists, skipping...")
        return root_element, resource_node_ids
    
    nic = network_client.network_interfaces.get(rg.name, resource.name)
    print(f"Added NIC {nic.name}")
    nic_id = f"{nic.name}_{uuid.uuid4()}"
    resource_node_ids[nic.name] = nic_id
    nic_node = SubElement(root_element, 'mxCell', {'id': nic_id, 'value': nic.name, 'vertex': '1', 'parent': '1'})
    nic_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids