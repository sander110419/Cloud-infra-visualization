from azure.mgmt.containerservice import ContainerServiceClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_kubernetes_service(resource, rg, kubernetes_client, root_element, resource_node_ids):
    # Get the Kubernetes Service
    kubernetes_service = kubernetes_client.managed_clusters.get(rg.name, resource.name)
    
    print(f"Added Kubernetes Service {kubernetes_service.name}")
    kubernetes_service_id = f"{kubernetes_service.name}_{uuid.uuid4()}"
    resource_node_ids[kubernetes_service_id] = kubernetes_service_id  # Use the Kubernetes Service name as the key
    kubernetes_service_node = SubElement(root_element, 'mxCell', {'id': kubernetes_service_id, 'value': kubernetes_service.name, 'vertex': '1', 'parent': '1'})
    kubernetes_service_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
