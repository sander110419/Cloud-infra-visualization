from azure.mgmt.monitor import MonitorManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_monitor_action_group(resource, rg, monitor_client, root_element, resource_node_ids):
    action_group = monitor_client.action_groups.get(rg.name, resource.name)
    print(f"Added Monitor Action Group {action_group.name}")
    action_group_id = f"{action_group.name}_{uuid.uuid4()}"
    resource_node_ids[action_group.name] = action_group_id
    action_group_node = SubElement(root_element, 'mxCell', {'id': action_group_id, 'value': action_group.name, 'vertex': '1', 'parent': '1'})
    action_group_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
