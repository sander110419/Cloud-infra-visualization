from azure.mgmt.botservice import AzureBotService
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_bot_service(resource, rg, bot_service_client, root_element, resource_node_ids):
    # Get the Bot Service
    bot_service = bot_service_client.bots.get(rg.name, resource.name)
    
    print(f"Added Bot Service {bot_service.name}")
    bot_service_id = f"{bot_service.name}_{uuid.uuid4()}"
    resource_node_ids[bot_service_id] = bot_service_id  # Use the Bot Service name as the key
    bot_service_node = SubElement(root_element, 'mxCell', {'id': bot_service_id, 'value': bot_service.name, 'vertex': '1', 'parent': '1'})
    bot_service_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
