from azure.mgmt.dns import DnsManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_dns_zone(resource, rg, dns_client, root_element, resource_node_ids):
    dns_zone = dns_client.zones.get(rg.name, resource.name)
    print(f"Added DNS Zone {dns_zone.name}")
    dns_id = f"{dns_zone.name}_{uuid.uuid4()}"
    resource_node_ids[dns_zone.name] = dns_id
    dns_node = SubElement(root_element, 'mxCell', {'id': dns_id, 'value': dns_zone.name, 'vertex': '1', 'parent': '1'})
    dns_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
