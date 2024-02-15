from azure.mgmt.compute import ComputeManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_virtual_machine(resource, rg, compute_client, root_element, resource_node_ids):
    vm = compute_client.virtual_machines.get(rg.name, resource.name)
    print(f"Added VM {vm.name}")
    vm_id = f"{vm.name}_{uuid.uuid4()}"
    resource_node_ids[vm.name] = vm_id
    vm_node = SubElement(root_element, 'mxCell', {'id': vm_id, 'value': vm.name, 'vertex': '1', 'parent': '1'})
    vm_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids