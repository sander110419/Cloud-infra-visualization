from azure.mgmt.servicefabric import ServiceFabricManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_service_fabric_cluster(resource, rg, sf_client, root_element, resource_node_ids):
    sf_cluster = sf_client.clusters.get(rg.name, resource.name)
    print(f"Added Service Fabric Cluster {sf_cluster.name}")
    sf_id = f"{sf_cluster.name}_{uuid.uuid4()}"
    resource_node_ids[sf_cluster.name] = sf_id
    sf_node = SubElement(root_element, 'mxCell', {'id': sf_id, 'value': sf_cluster.name, 'vertex': '1', 'parent': '1'})
    sf_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
