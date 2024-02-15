from azure.mgmt.machinelearningservices import MachineLearningServicesManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_ml_workspace(resource, rg, ml_client, root_element, resource_node_ids):
    # Get the Machine Learning Workspace
    ml_workspace = ml_client.workspaces.get(rg.name, resource.name)
    
    print(f"Added Machine Learning Workspace {ml_workspace.name}")
    ml_workspace_id = f"{ml_workspace.name}_{uuid.uuid4()}"
    resource_node_ids[ml_workspace_id] = ml_workspace_id  # Use the Machine Learning Workspace name as the key
    ml_workspace_node = SubElement(root_element, 'mxCell', {'id': ml_workspace_id, 'value': ml_workspace.name, 'vertex': '1', 'parent': '1'})
    ml_workspace_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
