import sys
import json
import xml.etree.ElementTree as ET

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

# Create a dictionary to store all resources
all_resources = {}

# Create a set to store unique ids
unique_ids = set()

# Define the default edge (line) syle between resources
edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;"

# Iterate over the objects in the JSON data to populate the all_resources dictionary
for subscription_id, resource_groups in data['Objects'].items():
    for resource_group, resources in resource_groups.items():
        for resource in resources:
            details = resource['Details']
            if isinstance(details, dict):
                details = [details]  # Make it a list to unify the handling

            for detail in details:
                # Check if 'id' exists in detail
                if 'id' not in detail:
                    print(f"Warning: Missing 'id' in detail: {detail}")
                    continue  # Skip this detail

                # Store the resource detail using its id as the key
                all_resources[detail['id']] = detail

# Define initial positions and increments
initial_x = 360
initial_y = 540
x_increment = 150
y_increment = 100

# Initialize current positions
current_x = initial_x
current_y = initial_y

# Iterate over the objects in the JSON data again to create the nodes and edges
for subscription_id, resource_groups in data['Objects'].items():
    for resource_group, resources in resource_groups.items():
        # Create a node for the resource group
        rg_node = ET.SubElement(root, 'mxCell', {
            'id': f"sub-{subscription_id}-rg-{resource_group}",
            'value': resource_group,
            'style': "rounded=0;whiteSpace=wrap;html=1;",
            'vertex': "1",
            'parent': "1"
        })
        ET.SubElement(rg_node, 'mxGeometry', {'x': str(current_x), 'y': str(current_y), 'width': "120", 'height': "60", 'as': "geometry"})

        # Update the current position for the next node
        current_y += y_increment

        for resource in resources:
            details = resource['Details']
            if isinstance(details, dict):
                details = [details]  # Make it a list to unify the handling

            for i, detail in enumerate(details):
                # Check if 'id' exists in detail
                if 'id' not in detail:
                    print(f"Warning: Missing 'id' in detail: {detail}")
                    continue  # Skip this detail

                # If the id is already in the set, skip this detail
                if detail['id'] in unique_ids:
                    print(f"Warning: Duplicate 'id' found: {detail['id']}")
                    continue

                # Add the id to the set
                unique_ids.add(detail['id'])

                # Create a node for each resource detail
                resource_node = ET.SubElement(root, 'mxCell', {
                    'id': f"resource-{detail['id']}",
                    'value': detail['name'],
                    'style': "rounded=0;whiteSpace=wrap;html=1;",
                    'vertex': "1",
                    'parent': "1"
                })
                ET.SubElement(resource_node, 'mxGeometry', {'x': str(current_x), 'y': str(current_y), 'width': "120", 'height': "60", 'as': "geometry"})

                # Update the current position for the next node
                current_y += y_increment

                # Create an edge between the resource group and the resource
                edge = ET.SubElement(root, 'mxCell', {
                    'style': edge_style,
                    'edge': "1",
                    'parent': "1",
                    'source': f"sub-{subscription_id}-rg-{resource_group}",
                    'target': f"resource-{detail['id']}"
                })
                edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a database, create an edge to its server
                if detail['type'] == "Microsoft.Sql/servers/databases":
                    server_id = '/'.join(detail['id'].split('/')[:-2])  # Extract the server id from the database id
                    server_edge = ET.SubElement(root, 'mxCell', {
                        'style': edge_style,
                        'edge': "1",
                        'parent': "1",
                        'source': f"resource-{server_id}",
                        'target': f"resource-{detail['id']}"
                    })
                    server_edge_geometry = ET.SubElement(server_edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                    server_points = ET.SubElement(server_edge_geometry, 'Array', {'as': "points"})
                    ET.SubElement(server_points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a web app, create an edge to its app service plan
                if resource['ResourceType'] == "Microsoft.Web/sites":
                    server_farm_id = detail['server_farm_id']
                    if server_farm_id in all_resources:
                        edge = ET.SubElement(root, 'mxCell', {
                            'style': edge_style,
                            'edge': "1",
                            'parent': "1",
                            'source': f"resource-{detail['id']}",
                            'target': f"resource-{server_farm_id}"
                        })
                        edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                        points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                        ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a disk, create an edge to its VM
                if resource['ResourceType'] == "Microsoft.Compute/disks":
                    if 'managed_by' in detail:
                        vm_id = detail['managed_by']
                    else:
                        vm_id = None  # or some default value
                    if vm_id in all_resources:
                        edge = ET.SubElement(root, 'mxCell', {
                            'style': edge_style,
                            'edge': "1",
                            'parent': "1",
                            'source': f"resource-{detail['id']}",
                            'target': f"resource-{vm_id}"
                        })
                        edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                        points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                        ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a VM, create an edge to its NIC
                if resource['ResourceType'] == "Microsoft.Compute/virtualMachines":
                    if 'network_profile' in detail and 'network_interfaces' in detail['network_profile']:
                        nic_id = detail['network_profile']['network_interfaces'][0]['id']
                        if nic_id in all_resources:
                            edge = ET.SubElement(root, 'mxCell', {
                                'style': edge_style,
                                'edge': "1",
                                'parent': "1",
                                'source': f"resource-{detail['id']}",
                                'target': f"resource-{nic_id}"
                            })
                            edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                            points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                            ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a VM, create an edge to its NIC and its extensions
                if resource['ResourceType'] == "Microsoft.Compute/virtualMachines":
                    if 'network_profile' in detail and 'network_interfaces' in detail['network_profile']:
                        nic_id = detail['network_profile']['network_interfaces'][0]['id']
                        if nic_id in all_resources:
                            edge = ET.SubElement(root, 'mxCell', {
                                'style': edge_style,
                                'edge': "1",
                                'parent': "1",
                                'source': f"resource-{detail['id']}",
                                'target': f"resource-{nic_id}"
                            })
                            edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                            points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                            ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                    # Create an edge to each of its extensions
                    if 'resources' in detail:
                        for ext in detail['resources']:
                            ext_id = ext['id']
                            if ext_id in all_resources:
                                edge = ET.SubElement(root, 'mxCell', {
                                    'style': edge_style,
                                    'edge': "1",
                                    'parent': "1",
                                    'source': f"resource-{detail['id']}",
                                    'target': f"resource-{ext_id}"
                                })
                                edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                                points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                                ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a Private Endpoint, create an edge to its NIC
                if resource['ResourceType'] == "Microsoft.Network/privateEndpoints":
                    if 'network_interfaces' in detail:
                        for nic in detail['network_interfaces']:
                            nic_id = nic['id']
                            if nic_id in all_resources:
                                edge = ET.SubElement(root, 'mxCell', {
                                    'style': edge_style,
                                    'edge': "1",
                                    'parent': "1",
                                    'source': f"resource-{detail['id']}",
                                    'target': f"resource-{nic_id}"
                                })
                                edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                                points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                                ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})
                    if resource['ResourceType'] == "Microsoft.Compute/disks":
                        if 'managed_by' in detail:
                            vm_id = detail['managed_by']

# Write the XML to a file
tree = ET.ElementTree(mxfile)
tree.write(xml_output_path)
