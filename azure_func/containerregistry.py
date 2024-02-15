from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_container_registry(resource, rg, container_registry_client, root_element, resource_node_ids):
    # Get the Container Registry
    container_registry = container_registry_client.registries.get(rg.name, resource.name)
    
    print(f"Added Container Registry {container_registry.name}")
    container_registry_id = f"{container_registry.name}_{uuid.uuid4()}"
    resource_node_ids[container_registry_id] = container_registry_id  # Use the Container Registry name as the key
    container_registry_node = SubElement(root_element, 'mxCell', {'id': container_registry_id, 'value': container_registry.name, 'vertex': '1', 'parent': '1'})
    container_registry_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
