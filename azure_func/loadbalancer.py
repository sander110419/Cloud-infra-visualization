from lxml.etree import Element, SubElement, tostring
import uuid

def handle_load_balancer(resource, rg, network_client, root_element, resource_node_ids):
    # Get the Load Balancer
    load_balancer = network_client.load_balancers.get(rg.name, resource.name)
    
    print(f"Added Load Balancer {load_balancer.name}")
    load_balancer_id = f"{load_balancer.name}_{uuid.uuid4()}"
    resource_node_ids[load_balancer_id] = load_balancer_id  # Use the Load Balancer name as the key
    load_balancer_node = SubElement(root_element, 'mxCell', {'id': load_balancer_id, 'value': load_balancer.name, 'vertex': '1', 'parent': '1'})
    load_balancer_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids