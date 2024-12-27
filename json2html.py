import os
import json
import base64


ICON_MAPPING = {
    'virtualMachines': 'Virtual-Machine.svg',
    'networkInterfaces': 'Network-Interfaces.svg',
    'storageAccounts': 'Storage-Accounts.svg',
    'virtualNetworks': 'Virtual-Networks.svg',
    'publicIPAddresses': 'Public-IP-Addresses.svg',
    'networkSecurityGroups': 'Network-Security-Groups.svg',
    'loadBalancers': 'Load-Balancers.svg',
    'disks': 'Disks.svg',
    'snapshots': 'Disks-Snapshots.svg',
    'cosmosDB': 'Azure-Cosmos-DB.svg',
    'sqlServers': 'SQL-Server.svg',
    'sqlDatabases': 'SQL-Database.svg',
    'vaults': 'Key-Vaults.svg',
    'appServicePlans': 'App-Service-Plans.svg',
    'webSites': 'App-Services.svg',
    'functionApps': 'Function-Apps.svg',
    'apiManagementServices': 'API-Management-Services.svg',
    'dataLakeStores': 'Data-Lake-Store-Gen1.svg',
    'dataFactories': 'Data-Factories.svg',
    'streamingJobs': 'Stream-Analytics-Jobs.svg',
    'managedClusters': 'Kubernetes-Services.svg',
    'searchServices': 'Search.svg',
    'signalR': 'SignalR.svg',
    'botServices': 'Bot-Services.svg',
    'iotHubs': 'IoT-Hub.svg',
    'cognitiveServices': 'Cognitive-Services.svg',
    'cdns': 'CDN-Profiles.svg',
    'serviceFabricClusters': 'Service-Fabric-Clusters.svg',
    'schedules': 'Scheduler.svg',
    'actionGroups': 'Action-Groups.svg',
    'jobCollections': 'Scheduler-Job-Collections.svg',
    'databaseAccounts': 'Azure-Cosmos-DB.svg',
    'eventSubscriptions': 'Event-Grid-Subscriptions.svg',
    'eventGridTopics': 'Event-Grid-Topics.svg',
    'recoveryServicesVaults': 'Recovery-Services-Vaults.svg',
    'privateEndpoints': 'Private-Endpoints.svg',
    'proximityPlacementGroups': 'Proximity-Placement-Groups.svg',
    'containerApps': 'Container-Apps-Environments.svg',
    'eventHubNamespaces': 'Event-Hubs.svg',
    'eventHubs': 'Event-Hubs.svg',
    'workflows': 'Logic-Apps.svg',
    'containerRegistries': 'Container-Registries.svg',
    'serviceBusNamespaces': 'Azure-Service-Bus.svg',
    'containerGroups': 'Container-Instances.svg',
    'storageSyncServices': 'Storage-Sync-Services.svg',
    'communicationServices': 'Azure-Communication-Services.svg',
    'restorePointCollections': 'Restore-Points-Collections.svg',
    'routeTables': 'Route-Tables.svg',
    'actionRules': 'Action-Groups.svg',
    'alerts': 'Alerts.svg',
    'metricAlerts': 'Alerts.svg',
    'scheduledQueryRules': 'Log-Analytics-Query-Pack.svg',
    'applicationGatewayWAFPolicies': 'Web-Application-Firewall-Policies(WAF).svg',
    'afdProfiles': 'Front-Door-and-CDN-Profiles.svg',
    'frontDoors': 'Front-Door-and-CDN-Profiles.svg',
    'afdEndpoints': 'Front-Door-and-CDN-Profiles.svg',
    'eventGridDomains': 'Event-Grid-Domains.svg',
    'serviceBusQueues': 'Azure-Service-Bus.svg',
    'serviceBusTopics': 'Azure-Service-Bus.svg',
    'managementLocks': 'Management-Groups.svg',
    'sqlManagedInstances': 'SQL-Managed-Instance.svg',
    'sqlManagedDatabases': 'SQL-Database.svg',
    'privateLinkServices': 'Private-Link-Services.svg',
    'integrationAccounts': 'Integration-Accounts.svg',
    'virtualClusters': 'Virtual-Clusters.svg',
    'serviceEndpointPolicies': 'Service-Endpoint-Policies.svg',
    'imageGalleries': 'Shared-Image-Galleries.svg',
    'galleryImages': 'Images.svg',
    'galleryImageVersions': 'VM-Image-Version.svg',
    'vmImages': 'VM-Images-(Classic).svg',
    'webCertificates': 'App-Service-Certificates.svg',
    'webConnections': 'Connections.svg',
    'smartDetectorAlertRules': 'Alerts.svg',
    'applicationGateways': 'Application-Gateways.svg',
    'applicationSecurityGroups': 'Application-Security-Groups.svg',
    'automationAccounts': 'Automation-Accounts.svg',
    'availabilitySets': 'Availability-Sets.svg',
    'backupPolicies': 'Azure-Backup-Center.svg',
    'bastionHosts': 'Bastions.svg',
    'batchAccounts': 'Batch-Accounts.svg',
    'blueprints': 'Blueprints.svg',
    'firewalls': 'Firewalls.svg',
    'ddosProtectionPlans': 'DDoS-Protection-Plans.svg',
    'dnsZones': 'DNS-Zones.svg',
    'expressRouteCircuits': 'ExpressRoute-Circuits.svg',
    'networkWatchers': 'Network-Watcher.svg',
    'trafficmanagerprofiles': 'Traffic-Manager-Profiles.svg',
    'serverFarms': 'App-Service-Plans.svg',
    'workspaces': 'Log-Analytics-Workspaces.svg',
    'components': 'Function-Apps.svg',
    'actiongroups': 'Detonation.svg',
    'alertRules': 'Alerts.svg',
    'activityLogAlerts': 'Alerts.svg',
    'b2cDirectories': 'Azure-AD-B2C.svg',
    'userAssignedIdentities': 'Entra-Managed-Identities.svg',
    'flexibleServers': 'SQL-Server.svg',
    'Resource Group': 'Resource-Groups.svg',
    'Subscriptions': 'Subscriptions.svg',
}

def encode_svg_icon_to_base64(icon_filename):
    icon_path = os.path.join('icons', icon_filename)
    with open(icon_path, 'rb') as svg_file:
        svg_data = svg_file.read()
        base64_encoded = base64.b64encode(svg_data).decode('utf-8')
        data_uri = f"data:image/svg+xml;base64,{base64_encoded}"
        return data_uri
    
def get_resource_name(details):
    if isinstance(details, dict):
        return str(details.get('name', 'Unknown'))
    elif isinstance(details, list) and details:
        # If Details is a list, try to get name from first item
        if isinstance(details[0], dict):
            return str(details[0].get('name', 'Unknown'))
    return 'Unknown'

# json2mermaid.py

def generate_cytoscape_elements(data):
    elements = []
    
    for subscription_id, subscription_data in data['Objects'].items():
        sub_id = f"sub_{subscription_id.replace('-', '_').replace(' ', '_')}"
        # Add subscription node
        elements.append({
            'data': {
                'id': sub_id,
                'label': f'Subscription: {subscription_id}',
                'type': 'subscription',
                'icon': encode_svg_icon_to_base64('Subscriptions.svg')
            }
        })
        
        for rg_name, resources in subscription_data.items():
            rg_id = f"rg_{rg_name.replace('-', '_').replace(' ', '_')}"
            # Add resource group node
            elements.append({
                'data': {
                    'id': rg_id,
                    'label': f'Resource Group: {rg_name}',
                    'type': 'resourceGroup',
                    'icon': encode_svg_icon_to_base64('Resource-Groups.svg')
                }
            })
            # Add edge from subscription to resource group
            elements.append({
                'data': {
                    'id': f'{sub_id}_to_{rg_id}',
                    'source': sub_id,
                    'target': rg_id
                }
            })
            
            for resource in resources:
                resource_name = get_resource_name(resource['Details'])
                resource_type_full = resource['ResourceType']
                resource_type_parts = resource_type_full.split('/')
                resource_type_key = resource_type_parts[-1] if len(resource_type_parts) >= 2 else resource_type_full
                
                icon_filename = ICON_MAPPING.get(resource_type_key)
                if icon_filename:
                    icon_data_uri = encode_svg_icon_to_base64(icon_filename)
                else:
                    icon_data_uri = None  # No icon available
                
                resource_id = f"res_{resource_name.replace('-', '_').replace(' ', '_')}"
                # Prepare node data
                node_data = {
                    'id': resource_id,
                    'label': f'{resource_type_key}: {resource_name}',
                    'type': 'resource',
                }
                if icon_data_uri:
                    node_data['icon'] = icon_data_uri
                # Add resource node
                elements.append({
                    'data': node_data
                })
                # Add edge from resource group to resource
                elements.append({
                    'data': {
                        'id': f'{rg_id}_to_{resource_id}',
                        'source': rg_id,
                        'target': resource_id
                    }
                })
        
    return elements

def generate_html(data):
    elements = generate_cytoscape_elements(data)
    
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Infrastructure Visualization</title>
        <!-- Cytoscape.js -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
        <!-- dagre.js (layout algorithm) -->
        <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script>
        <!-- cytoscape-dagre extension -->
        <script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #cy {{
                width: 100vw;
                height: 100vh;
                position: absolute;
                top: 0;
                left: 0;
            }}
        </style>
    </head>
    <body>
        <div id="cy"></div>
        <script>
            cytoscape.use(cytoscapeDagre);

            const elements = {elements};
            
            const cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: elements,
                style: [
                    // Default style for all nodes
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)',
                            'background-color': '#ffffff',
                            'shape': 'roundrectangle',
                            'border-width': 1,
                            'border-color': '#888',
                            'padding': '10px',
                            'text-wrap': 'wrap',
                            'text-max-width': '100px',
                            'font-size': '12px'
                        }}
                    }},
                    // Additional styles for nodes with an icon
                    {{
                        selector: 'node[icon]',
                        style: {{
                            'background-image': 'data(icon)',
                            'background-fit': 'contain',
                            'background-width': '60%',
                            'background-height': '60%',
                            'background-opacity': 0,
                            'background-color': '#ffffff'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 2,
                            'line-color': '#888',
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'target-arrow-color': '#888'
                        }}
                    }}
                ],
                layout: {{
                    name: 'dagre',
                    rankDir: 'LR',
                    padding: 50,
                    spacingFactor: 1.5
                }}
            }});
            
            // Fit the graph to the viewport
            cy.fit();
        </script>
    </body>
    </html>
    '''
    
    # Use json.dumps to correctly format the elements data
    html_content = html_template.format(elements=json.dumps(elements))
    return html_content