import os

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
    'b2cDirectories': 'Azure-Active-Directory-B2C.svg',
    'userAssignedIdentities': 'User-Assigned-Managed-Identities.svg',
    'flexibleServers': 'SQL-Server.svg'
}


def get_resource_name(details):
    if isinstance(details, dict):
        return str(details.get('name', 'Unknown'))
    elif isinstance(details, list) and details:
        # If Details is a list, try to get name from first item
        if isinstance(details[0], dict):
            return str(details[0].get('name', 'Unknown'))
    return 'Unknown'

# json2mermaid.py

def generate_mermaid_flowchart(data):
    mermaid_code = ["graph LR;"]  # Using Left to Right layout

    for subscription_id, subscription_data in data['Objects'].items():
        sub_id = f"sub_{subscription_id.replace('-', '_').replace(' ', '_')}"
        mermaid_code.append(f'{sub_id}["<b>Subscription:</b><br>{subscription_id}"]')

        for rg_name, resources in subscription_data.items():
            rg_id = f"rg_{rg_name.replace('-', '_').replace(' ', '_')}"
            mermaid_code.append(f'{rg_id}["<b>Resource Group:</b><br>{rg_name}"]')
            mermaid_code.append(f"{sub_id} --> {rg_id}")

            for resource in resources:
                # Get resource name and type
                resource_name = get_resource_name(resource['Details'])
                resource_type_full = resource['ResourceType']
                resource_type_parts = resource_type_full.split('/')
                # Handle cases where resource type may not have expected structure
                if len(resource_type_parts) >= 2:
                    resource_type_key = resource_type_parts[-1]
                else:
                    resource_type_key = resource_type_full

                # Map resource type to icon
                icon_filename = ICON_MAPPING.get(resource_type_key)
                if icon_filename:
                    icon_path = f'./icons/{icon_filename}'  # Adjust the path as necessary
                    icon_html = f'<img src="{icon_path}" width="48"/><br>'
                else:
                    icon_html = ''

                # Create node with icon
                resource_id = f"res_{resource_name.replace('-', '_').replace(' ', '_')}"
                resource_label = f"{icon_html}<b>{resource_type_key}:</b><br>{resource_name}"
                mermaid_code.append(f'{resource_id}["{resource_label}"]')
                mermaid_code.append(f"{rg_id} --> {resource_id}")

    return "\n".join(mermaid_code)


def generate_html(mermaid_code):
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Infrastructure Visualization</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            #container {{
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                position: relative;
            }}
            #mermaid {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform-origin: center center;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="mermaid">
                <pre class="mermaid">
{mermaid_code}
                </pre>
            </div>
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                securityLevel: 'loose',
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }}
            }});

            // Zooming and Panning Functionality
            (function() {{
                const container = document.getElementById('container');
                const mermaidDiv = document.getElementById('mermaid');
                let scale = 1;
                let translateX = 0;
                let translateY = 0;
                const zoomSensitivity = 0.01;

                function updateTransform() {{
                    mermaidDiv.style.transform = `translate(-50%, -50%) translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
                }}

                container.addEventListener('wheel', function(e) {{
                    e.preventDefault();
                    const delta = e.deltaY * zoomSensitivity;
                    const newScale = scale - delta;

                    // Keep the scale within reasonable bounds
                    if (newScale > 0.001 && newScale < 100) {{
                        scale = newScale;
                        updateTransform();
                    }}
                }});

                let isDragging = false;
                let startX = 0;
                let startY = 0;

                container.addEventListener('mousedown', function(e) {{
                    isDragging = true;
                    startX = e.clientX - translateX;
                    startY = e.clientY - translateY;
                    container.style.cursor = 'grabbing';
                }});

                container.addEventListener('mousemove', function(e) {{
                    if (!isDragging) return;
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    updateTransform();
                }});

                container.addEventListener('mouseup', function(e) {{
                    isDragging = false;
                    container.style.cursor = 'default';
                }});

                container.addEventListener('mouseleave', function(e) {{
                    isDragging = false;
                    container.style.cursor = 'default';
                }});
            }})();
        </script>
    </body>
    </html>
    '''
    return html_template.format(mermaid_code=mermaid_code)
