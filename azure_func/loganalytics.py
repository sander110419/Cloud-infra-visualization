from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_log_analytics_workspace(resource, rg, la_client, root_element, resource_node_ids):
    # Get the log analytics workspace
    log_analytics_workspace = la_client.workspaces.get(rg.name, resource.name)
    
    print(f"Added Log Analytics Workspace {log_analytics_workspace.name}")
    log_analytics_workspace_id = f"{log_analytics_workspace.name}_{uuid.uuid4()}"
    resource_node_ids[log_analytics_workspace_id] = log_analytics_workspace_id  # Use the log analytics workspace name as the key
    log_analytics_workspace_node = SubElement(root_element, 'mxCell', {'id': log_analytics_workspace_id, 'value': log_analytics_workspace.name, 'vertex': '1', 'parent': '1'})
    log_analytics_workspace_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
