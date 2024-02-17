from azure.mgmt.containerservice import ContainerServiceClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_aks_service(resource, rg, aks_client, root_element, resource_node_ids):
    # Get the AKS
    aks_service = aks_client.managed_clusters.get(rg.name, resource.name)
    
    print(f"Added AKS {aks_service.name}")
    aks_service_id = f"{aks_service.name}_{uuid.uuid4()}"
    resource_node_ids[aks_service_id] = aks_service_id  # Use the AKS name as the key
    aks_service_node = SubElement(root_element, 'mxCell', {'id': aks_service_id, 'value': aks_service.name, 'vertex': '1', 'parent': '1'})
    aks_service_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
