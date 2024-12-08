import sys
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import hashlib

def sanitize_id(resource_id):
    """Generate a unique and XML-friendly ID from the resource ID."""
    # Create a hash of the resource ID to ensure uniqueness and remove invalid characters
    return f"resource-{hashlib.md5(resource_id.encode('utf-8')).hexdigest()}"

def create_unique_id(resource_id, existing_ids):
    """Create a unique ID and ensure it hasn't been used before."""
    sanitized_id = sanitize_id(resource_id)
    counter = 1
    unique_id = sanitized_id
    while unique_id in existing_ids:
        unique_id = f"{sanitized_id}-{counter}"
        counter += 1
    existing_ids.add(unique_id)
    return unique_id

def determine_relationships(detail, resource_id, parent_child_map):
    """Determine all possible parent-child relationships for an Azure resource"""
    
    # SQL Server -> Database relationship
    if detail.get('type') == "Microsoft.Sql/servers/databases":
        server_id = '/'.join(resource_id.split('/')[:-2])
        if server_id in all_resources:
            parent_child_map[server_id].append(resource_id)
    
    # VM -> Managed Disk relationship
    if 'managed_by' in detail:
        parent_child_map[detail['managed_by']].append(resource_id)
    
    # Web App -> App Service Plan relationship
    if 'server_farm_id' in detail:
        parent_child_map[detail['server_farm_id']].append(resource_id)
    
    # VM -> NIC relationship
    if 'network_profile' in detail and 'network_profile' in detail and 'network_interfaces' in detail['network_profile']:
        for nic in detail['network_profile']['network_interfaces']:
            parent_child_map[resource_id].append(nic['id'])
    
    # VM -> Extensions relationship
    if 'resources' in detail:
        for ext in detail['resources']:
            parent_child_map[resource_id].append(ext['id'])
    
    # Private Endpoint -> NIC relationship
    if detail.get('type') == "Microsoft.Network/privateEndpoints" and 'network_interfaces' in detail:
        for nic in detail['network_interfaces']:
            parent_child_map[resource_id].append(nic['id'])
    
    # Storage Account -> File/Blob/Queue/Table Services
    if detail.get('type') == "Microsoft.Storage/storageAccounts":
        for service in ['blob', 'file', 'queue', 'table']:
            service_id = f"{resource_id}/{service}Services/default"
            if service_id in all_resources:
                parent_child_map[resource_id].append(service_id)
    
    # App Service -> Deployment Slots
    if detail.get('type') == "Microsoft.Web/sites":
        for slot in detail.get('slots', []):
            parent_child_map[resource_id].append(slot['id'])
    
    # Key Vault -> Keys/Secrets/Certificates
    if detail.get('type') == "Microsoft.KeyVault/vaults":
        for entity_type in ['keys', 'secrets', 'certificates']:
            for entity in detail.get(entity_type, []):
                parent_child_map[resource_id].append(entity['id'])
    
    # Load Balancer -> Backend Pools
    if detail.get('type') == "Microsoft.Network/loadBalancers":
        for pool in detail.get('backendAddressPools', []):
            parent_child_map[resource_id].append(pool['id'])
    
    # VNET -> Subnets
    if detail.get('type') == "Microsoft.Network/virtualNetworks":
        for subnet in detail.get('subnets', []):
            parent_child_map[resource_id].append(subnet['id'])
    
    # NIC -> IP Configurations
    if detail.get('type') == "Microsoft.Network/networkInterfaces":
        for ip_config in detail.get('ipConfigurations', []):
            parent_child_map[resource_id].append(ip_config['id'])
    
    # Application Gateway -> Backend Pools, HTTP Settings, etc.
    if detail.get('type') == "Microsoft.Network/applicationGateways":
        for component in ['backendAddressPools', 'backendHttpSettingsCollection', 'frontendIPConfigurations']:
            for item in detail.get(component, []):
                parent_child_map[resource_id].append(item['id'])

# Check if the correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: python json2xml.py <input.json> <output.xml>")
    sys.exit(1)

# Get the input and output file paths from the command-line arguments
json_file_path = sys.argv[1]
xml_output_path = sys.argv[2]

# Load the JSON data
with open(json_file_path) as f:
    data = json.load(f)

# Create the root elements of the XML file
mxfile = ET.Element('mxfile', {
    'host': "app.diagrams.net",
    'modified': "2024-04-16T13:19:21.268Z",
    'agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    'etag': "ml9OaWOclvuRr0KFJMIA",
    'version': "24.2.5",
    'type': "device"
})
diagram = ET.SubElement(mxfile, 'diagram', {'name': "Page-1", 'id': "1-vEf1LYnyZOLClbR_A6"})
mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {'dx': "2026", 'dy': "1111", 'grid': "1", 'gridSize': "10", 'guides': "1", 'tooltips': "1", 'connect': "1", 'arrows': "1", 'fold': "1", 'page': "1", 'pageScale': "1", 'pageWidth': "850", 'pageHeight': "1100", 'math': "0", 'shadow': "0"})
root = ET.SubElement(mxGraphModel, 'root')

# Add the default cells
ET.SubElement(root, 'mxCell', {'id': "0"})
ET.SubElement(root, 'mxCell', {'id': "1", 'parent': "0"})

# Create dictionaries and sets
all_resources = {}
parent_child_map = defaultdict(list)
resource_group_resources = defaultdict(list)
existing_ids = set()  # Set to keep track of all assigned IDs

# Define the default edge style
edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"

# First pass: Collect all resources
for subscription_id, resource_groups in data['Objects'].items():
    for resource_group, resources in resource_groups.items():
        for resource in resources:
            details = resource['Details']
            if isinstance(details, dict):
                details = [details]

            for detail in details:
                if isinstance(detail, dict) and 'Error' in detail:
                    continue
                if 'id' not in detail:
                    continue

                all_resources[detail['id']] = detail
                resource_group_resources[resource_group].append(detail['id'])

# Second pass: Determine parent-child relationships
for resource_id, detail in all_resources.items():
    determine_relationships(detail, resource_id, parent_child_map)

# Layout calculations
initial_x = 360
initial_y = 100
parent_spacing = 250
child_spacing = 150
vertical_spacing = 120
# Starting Y position for the first resource group
current_y = initial_y

# Create nodes and edges
for subscription_id, resource_groups in data['Objects'].items():
    for resource_group, resources in resource_groups.items():
        # Create resource group node
        rg_id = create_unique_id(f"sub-{subscription_id}-rg-{resource_group}", existing_ids)
        rg_node = ET.SubElement(root, 'mxCell', {
            'id': rg_id,
            'value': resource_group,
            'style': "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;",
            'vertex': "1",
            'parent': "1"
        })
        ET.SubElement(rg_node, 'mxGeometry', {
            'x': str(initial_x),
            'y': str(current_y),
            'width': "160",
            'height': "60",
            'as': "geometry"
        })

        # Identify parent nodes (nodes that have children or no relationships)
        parent_nodes = []
        child_nodes = set()

        for resource in resources:
            details = resource['Details']
            if isinstance(details, dict):
                details = [details]

            for detail in details:
                if 'id' not in detail:
                    continue

                resource_id = detail['id']
                is_child = False
                for parent_id, children in parent_child_map.items():
                    if resource_id in children:
                        is_child = True
                        child_nodes.add(resource_id)
                        break

                if not is_child:
                    parent_nodes.append(detail)

        # Position parent nodes below the resource group
        parent_y = current_y + vertical_spacing
        parent_x_start = initial_x - (len(parent_nodes) * parent_spacing) / 2

        for i, parent in enumerate(parent_nodes):
            parent_x = parent_x_start + (i * parent_spacing)

            # Create parent node
            parent_node_id = create_unique_id(parent['id'], existing_ids)
            parent_node = ET.SubElement(root, 'mxCell', {
                'id': parent_node_id,
                'value': parent['name'],
                'style': "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;",
                'vertex': "1",
                'parent': "1"
            })
            ET.SubElement(parent_node, 'mxGeometry', {
                'x': str(parent_x),
                'y': str(parent_y),
                'width': "140",
                'height': "60",
                'as': "geometry"
            })

            # Connect to resource group
            edge_id = create_unique_id(f"edge-{parent_node_id}-{rg_id}", existing_ids)
            edge = ET.SubElement(root, 'mxCell', {
                'id': edge_id,
                'style': edge_style,
                'edge': "1",
                'parent': "1",
                'source': parent_node_id,
                'target': rg_id
            })
            ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})

            # Position and create child nodes vertically below the parent
            if parent['id'] in parent_child_map:
                child_x = parent_x  # Align child nodes horizontally with the parent
                children = parent_child_map[parent['id']]
                child_y_start = parent_y + vertical_spacing  # Start just below the parent

                for j, child_id in enumerate(children):
                    if child_id not in all_resources:
                        continue

                    child = all_resources[child_id]
                    child_y = child_y_start + (j * child_spacing)  # Position children vertically

                    # Create child node
                    child_node_id = create_unique_id(child_id, existing_ids)
                    child_node = ET.SubElement(root, 'mxCell', {
                        'id': child_node_id,
                        'value': child['name'],
                        'style': "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;",
                        'vertex': "1",
                        'parent': "1"
                    })
                    ET.SubElement(child_node, 'mxGeometry', {
                        'x': str(child_x),
                        'y': str(child_y),
                        'width': "120",
                        'height': "60",
                        'as': "geometry"
                    })

                    # Connect child to parent
                    edge_id = create_unique_id(f"edge-{child_node_id}-{parent_node_id}", existing_ids)
                    edge = ET.SubElement(root, 'mxCell', {
                        'id': edge_id,
                        'style': edge_style,
                        'edge': "1",
                        'parent': "1",
                        'source': child_node_id,
                        'target': parent_node_id
                    })
                    ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})

        max_children = max(len(parent_child_map.get(parent['id'], [])) for parent in parent_nodes) if parent_nodes else 0
        current_y += vertical_spacing * 2 + max_children * child_spacing + vertical_spacing

# Write the XML to a file
tree = ET.ElementTree(mxfile)
tree.write(xml_output_path)
