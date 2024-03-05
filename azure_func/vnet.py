from azure.mgmt.network import NetworkManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_virtual_network(resource, rg, network_client, root_element, resource_node_ids):
    # Create a unique id for the virtual network
    vnet_id = f"{resource.name}_{uuid.uuid4()}"

    # Check if a VNet node with the same id already exists
    if vnet_id in resource_node_ids:
        print(f"VNet {vnet_id} already exists, skipping...")
        return root_element, resource_node_ids

    # Get the Virtual Network
    virtual_network = network_client.virtual_networks.get(rg.name, resource.name)
    
    print(f"Added Virtual Network {virtual_network.name}")
    resource_node_ids[vnet_id] = vnet_id  # Use the Virtual Network id as the key
    virtual_network_node = SubElement(root_element, 'mxCell', {'id': vnet_id, 'value': virtual_network.name, 'vertex': '1', 'parent': '1'})
    virtual_network_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    
    # Call the new function to handle subnets
    handle_subnets(virtual_network, vnet_id, root_element, resource_node_ids)

    return root_element, resource_node_ids

def handle_subnets(virtual_network, parent_id, root_element, resource_node_ids):
    for subnet in virtual_network.subnets:
        # Create a unique id for the subnet
        subnet_id = f"{subnet.name}_{uuid.uuid4()}"

        # Check if a Subnet node with the same id already exists
        if subnet_id in resource_node_ids:
            print(f"Subnet {subnet_id} already exists, skipping...")
            continue

        print(f"Added Subnet {subnet.name}")
        resource_node_ids[subnet_id] = subnet_id  # Use the Subnet id as the key
        subnet_node = SubElement(root_element, 'mxCell', {'id': subnet_id, 'value': subnet.name, 'vertex': '1', 'parent': parent_id})
        subnet_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))

        # Link the Subnet to the Virtual Network
        link_vnet_to_subnet(parent_id, subnet_id, root_element)
        
    try:
        # Get the VM
        vm = compute_client.virtual_machines.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        vm_dict = vm.as_dict()

        return vm_dict

    except Exception as e:
        return {'Error': str(e)}