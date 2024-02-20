from azure.mgmt.web import WebSiteManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_app_service(resource, rg, web_client, root_element, resource_node_ids):
    # Check if the server has already been added
    if resource.name in resource_node_ids:
        print(f"Server {resource.name} already exists.")
        return root_element, resource_node_ids
    # Check if resource.name contains a '/'
    if '/' in resource.name:
        # Split the resource name into app service plan name and web app name
        app_service_plan_name, web_app_name = resource.name.split('/')
    else:
        print(f"Resource name {resource.name} does not contain '/': {resource.name}")
        return root_element, resource_node_ids  # Return early if resource.name doesn't contain '/'

    # Get the web app
    web_app = web_client.web_apps.get(rg.name, web_app_name)
    
    print(f"Added App Service {web_app.name}")
    web_app_id = f"{app_service_plan_name}/{web_app.name}_{uuid.uuid4()}"
    resource_node_ids[web_app_id] = web_app_id  # Use the combined app service plan and web app name as the key
    web_app_node = SubElement(root_element, 'mxCell', {'id': web_app_id, 'value': web_app.name, 'vertex': '1', 'parent': '1'})
    web_app_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids