from azure.mgmt.iothub import IotHubClient

def handle_iot_hub(resource, rg, iot_hub_client, root_element, resource_node_ids):
    # Get the IoT Hub
    iot_hub = iot_hub_client.iot_hub_resource.get(rg.name, resource.name)
    
    print(f"Added IoT Hub {iot_hub.name}")
    iot_hub_id = f"{iot_hub.name}_{uuid.uuid4()}"
    resource_node_ids[iot_hub_id] = iot_hub_id  # Use the IoT Hub name as the key
    iot_hub_node = SubElement(root_element, 'mxCell', {'id': iot_hub_id, 'value': iot_hub.name, 'vertex': '1', 'parent': '1'})
    iot_hub_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
