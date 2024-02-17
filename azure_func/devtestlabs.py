from azure.mgmt.devtestlabs import DevTestLabsClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_devtest_lab(resource, rg, devtest_client, root_element, resource_node_ids):
    devtest_lab = devtest_client.labs.get(rg.name, resource.name)
    print(f"Added DevTest Lab {devtest_lab.name}")
    devtest_id = f"{devtest_lab.name}_{uuid.uuid4()}"
    resource_node_ids[devtest_lab.name] = devtest_id
    devtest_node = SubElement(root_element, 'mxCell', {'id': devtest_id, 'value': devtest_lab.name, 'vertex': '1', 'parent': '1'})
    devtest_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids