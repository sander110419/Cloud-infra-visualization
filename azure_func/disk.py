from azure.mgmt.compute import ComputeManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_disk(resource, rg, compute_client, root_element, resource_node_ids):
    # Check if a Disk node with the same name already exists
    if resource.name in resource_node_ids:
        print(f"Disk {resource.name} already exists, skipping...")
        return root_element, resource_node_ids
    disk = compute_client.disks.get(rg.name, resource.name)
    print(f"Added Disk {disk.name}")
    disk_id = f"{disk.name}_{uuid.uuid4()}"
    resource_node_ids[disk.name] = disk_id
    disk_node = SubElement(root_element, 'mxCell', {'id': disk_id, 'value': disk.name, 'vertex': '1', 'parent': '1'})
    disk_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids