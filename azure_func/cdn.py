from azure.mgmt.cdn import CdnManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_cdn_profile(resource, rg, cdn_client, root_element, resource_node_ids):
    cdn_profile = cdn_client.profiles.get(rg.name, resource.name)
    print(f"Added CDN Profile {cdn_profile.name}")
    cdn_id = f"{cdn_profile.name}_{uuid.uuid4()}"
    resource_node_ids[cdn_profile.name] = cdn_id
    cdn_node = SubElement(root_element, 'mxCell', {'id': cdn_id, 'value': cdn_profile.name, 'vertex': '1', 'parent': '1'})
    cdn_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
