from azure.mgmt.web import WebSiteManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_app_service_plan(resource, rg, web_client, root_element, resource_node_ids):
    # Check if the App Service Plan has already been added
    if resource.name in resource_node_ids:
        print(f"App Service Plan {resource.name} already exists.")
        return root_element, resource_node_ids

    app_service_plan = web_client.app_service_plans.get(rg.name, resource.name)
    print(f"Added App Service Plan {app_service_plan.name}")
    app_service_plan_id = f"{app_service_plan.name}_{uuid.uuid4()}"
    resource_node_ids[app_service_plan.name] = app_service_plan_id
    app_service_plan_node = SubElement(root_element, 'mxCell', {'id': app_service_plan_id, 'value': app_service_plan.name, 'vertex': '1', 'parent': '1'})
    app_service_plan_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids