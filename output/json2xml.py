import json
import xml.etree.ElementTree as ET

# Load the JSON data
with open('./output/output.json') as f:
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

# Iterate over the objects in the JSON data
for subscription_id, resource_groups in data['Objects'].items():
    for resource_group, resources in resource_groups.items():
        # Create a node for the resource group
        rg_node = ET.SubElement(root, 'mxCell', {
            'id': f"rg-{resource_group}",
            'value': resource_group,
            'style': "rounded=0;whiteSpace=wrap;html=1;",
            'vertex': "1",
            'parent': "1"
        })
        ET.SubElement(rg_node, 'mxGeometry', {'x': "360", 'y': "540", 'width': "120", 'height': "60", 'as': "geometry"})

        for resource in resources:
            details = resource['Details']
            if isinstance(details, dict):
                details = [details]  # Make it a list to unify the handling

            for detail in details:
                # Create a node for each resource detail
                resource_node = ET.SubElement(root, 'mxCell', {
                    'id': f"resource-{detail['id']}",
                    'value': detail['name'],
                    'style': "rounded=0;whiteSpace=wrap;html=1;",
                    'vertex': "1",
                    'parent': "1"
                })
                ET.SubElement(resource_node, 'mxGeometry', {'x': "360", 'y': "650", 'width': "120", 'height': "60", 'as': "geometry"})

                # Create an edge between the resource group and the resource
                edge = ET.SubElement(root, 'mxCell', {
                    'style': "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;",
                    'edge': "1",
                    'parent': "1",
                    'source': f"rg-{resource_group}",
                    'target': f"resource-{detail['id']}"
                })
                edge_geometry = ET.SubElement(edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                points = ET.SubElement(edge_geometry, 'Array', {'as': "points"})
                ET.SubElement(points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a database, create an edge to its server
                if detail['type'] == "Microsoft.Sql/servers/databases":
                    server_id = '/'.join(detail['id'].split('/')[:-2])  # Extract the server id from the database id
                    server_edge = ET.SubElement(root, 'mxCell', {
                        'style': "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;",
                        'edge': "1",
                        'parent': "1",
                        'source': f"resource-{server_id}",
                        'target': f"resource-{detail['id']}"
                    })
                    server_edge_geometry = ET.SubElement(server_edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                    server_points = ET.SubElement(server_edge_geometry, 'Array', {'as': "points"})
                    ET.SubElement(server_points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a web app, create an edge to its app service plan
                if detail['type'] == "Microsoft.Web/sites":
                    server_id = '/'.join(detail['id'].split('/')[:-2])  # Extract the server id from the web app id
                    server_edge = ET.SubElement(root, 'mxCell', {
                        'style': "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;",
                        'edge': "1",
                        'parent': "1",
                        'source': f"resource-{server_id}",
                        'target': f"resource-{detail['id']}"
                    })
                    server_edge_geometry = ET.SubElement(server_edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                    server_points = ET.SubElement(server_edge_geometry, 'Array', {'as': "points"})
                    ET.SubElement(server_points, 'mxPoint', {'x': "0", 'y': "0"})

                # If the resource is a VM, create edges to its disk and NIC
                if detail['type'] == "Microsoft.Compute/virtualMachines":
                    for related_resource in detail['properties']['storageProfile']['dataDisks']:
                        disk_id = related_resource['managedDisk']['id']
                        disk_edge = ET.SubElement(root, 'mxCell', {
                            'style': "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;",
                            'edge': "1",
                            'parent': "1",
                            'source': f"resource-{detail['id']}",
                            'target': f"resource-{disk_id}"
                        })
                        disk_edge_geometry = ET.SubElement(disk_edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                        disk_points = ET.SubElement(disk_edge_geometry, 'Array', {'as': "points"})
                        ET.SubElement(disk_points, 'mxPoint', {'x': "0", 'y': "0"})

                    nic_id = detail['properties']['networkProfile']['networkInterfaces'][0]['id']
                    nic_edge = ET.SubElement(root, 'mxCell', {
                        'style': "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;",
                        'edge': "1",
                        'parent': "1",
                        'source': f"resource-{detail['id']}",
                        'target': f"resource-{nic_id}"
                    })
                    nic_edge_geometry = ET.SubElement(nic_edge, 'mxGeometry', {'relative': "1", 'as': "geometry"})
                    nic_points = ET.SubElement(nic_edge_geometry, 'Array', {'as': "points"})
                    ET.SubElement(nic_points, 'mxPoint', {'x': "0", 'y': "0"})

# Write the XML to a file
tree = ET.ElementTree(mxfile)
tree.write('./output/output.xml')