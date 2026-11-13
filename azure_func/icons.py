"""Icons, display names and categories for Azure resource types.

Every resource type gets an icon: first from the explicit table below, then
from its resource provider, and finally a generic one. Nothing here limits
which resources are collected - an unknown type is simply drawn with the
generic icon and a name derived from its type.
"""
import base64
import functools
import os
import re
import sys

from azure_func.drawio_library import LIBRARY_ICONS, LIBRARY_PREFIX

DEFAULT_ICON = "Resource-Explorer"

# lower-case resource type -> (icon file stem, display name)
RESOURCE_TYPES = {
    # --- compute ---------------------------------------------------------
    "microsoft.compute/virtualmachines": ("Virtual-Machine", "Virtual machine"),
    "microsoft.compute/virtualmachines/extensions": ("Extensions", "VM extension"),
    "microsoft.compute/virtualmachinescalesets": ("VM-Scale-Sets", "VM scale set"),
    "microsoft.compute/disks": ("Disks", "Managed disk"),
    "microsoft.compute/snapshots": ("Disks-Snapshots", "Disk snapshot"),
    "microsoft.compute/images": ("Images", "VM image"),
    "microsoft.compute/galleries": ("Azure-Compute-Galleries", "Compute gallery"),
    "microsoft.compute/galleries/images": ("Image-Definitions", "Image definition"),
    "microsoft.compute/galleries/images/versions": ("Image-Versions", "Image version"),
    "microsoft.compute/availabilitysets": ("Availability-Sets", "Availability set"),
    "microsoft.compute/proximityplacementgroups": ("Proximity-Placement-Groups", "Proximity placement group"),
    "microsoft.compute/diskencryptionsets": ("Disk-Encryption-Sets", "Disk encryption set"),
    "microsoft.compute/sshpublickeys": ("SSH-Keys", "SSH key"),
    "microsoft.compute/restorepointcollections": ("Restore-Points-Collections", "Restore point collection"),
    "microsoft.compute/hostgroups": ("Host-Groups", "Dedicated host group"),
    "microsoft.compute/hostgroups/hosts": ("Hosts", "Dedicated host"),
    "microsoft.compute/capacityreservationgroups": ("Capacity-Reservation-Groups", "Capacity reservation group"),
    "microsoft.compute/cloudservices": ("Cloud-Services-(extended-support)", "Cloud service"),
    "microsoft.classiccompute/virtualmachines": ("Virtual-Machines-(Classic)", "Virtual machine (classic)"),
    "microsoft.classiccompute/domainnames": ("Cloud-Services-(Classic)", "Cloud service (classic)"),
    "microsoft.hybridcompute/machines": ("Arc-Machines", "Arc-enabled server"),
    "microsoft.hybridcompute/machines/extensions": ("Extensions", "Arc machine extension"),
    "microsoft.maintenance/maintenanceconfigurations": ("Maintenance-Configuration", "Maintenance configuration"),
    "microsoft.virtualmachineimages/imagetemplates": ("Image-Templates", "Image template"),
    "microsoft.sqlvirtualmachine/sqlvirtualmachines": ("Azure-SQL-VM", "SQL virtual machine"),
    "microsoft.batch/batchaccounts": ("Batch-Accounts", "Batch account"),
    "microsoft.desktopvirtualization/hostpools": ("Host-Pools", "AVD host pool"),
    "microsoft.desktopvirtualization/applicationgroups": ("Application-Group", "AVD application group"),
    "microsoft.desktopvirtualization/workspaces": ("Workspaces", "AVD workspace"),
    "microsoft.desktopvirtualization/scalingplans": ("Azure-Virtual-Desktop", "AVD scaling plan"),
    "microsoft.avs/privateclouds": ("Azure-VMware-Solution", "Azure VMware Solution"),
    # --- networking ------------------------------------------------------
    "microsoft.network/virtualnetworks": ("Virtual-Networks", "Virtual network"),
    "microsoft.network/virtualnetworks/subnets": ("Subnet", "Subnet"),
    "microsoft.network/virtualnetworks/virtualnetworkpeerings": ("Peerings", "VNet peering"),
    "microsoft.network/networkinterfaces": ("Network-Interfaces", "Network interface"),
    "microsoft.network/networksecuritygroups": ("Network-Security-Groups", "Network security group"),
    "microsoft.network/applicationsecuritygroups": ("Application-Security-Groups", "Application security group"),
    "microsoft.network/publicipaddresses": ("Public-IP-Addresses", "Public IP address"),
    "microsoft.network/publicipprefixes": ("Public-IP-Prefixes", "Public IP prefix"),
    "microsoft.network/customipprefixes": ("Custom-IP-Prefix", "Custom IP prefix"),
    "microsoft.network/loadbalancers": ("Load-Balancers", "Load balancer"),
    "microsoft.network/applicationgateways": ("Application-Gateways", "Application gateway"),
    "microsoft.network/applicationgatewaywebapplicationfirewallpolicies": ("Web-Application-Firewall-Policies(WAF)", "WAF policy"),
    "microsoft.network/frontdoorwebapplicationfirewallpolicies": ("Web-Application-Firewall-Policies(WAF)", "Front Door WAF policy"),
    "microsoft.network/frontdoors": ("Front-Door-and-CDN-Profiles", "Front Door (classic)"),
    "microsoft.network/azurefirewalls": ("Firewalls", "Azure Firewall"),
    "microsoft.network/firewallpolicies": ("Azure-Firewall-Policy", "Firewall policy"),
    "microsoft.network/bastionhosts": ("Bastions", "Bastion"),
    "microsoft.network/virtualnetworkgateways": ("Virtual-Network-Gateways", "Virtual network gateway"),
    "microsoft.network/localnetworkgateways": ("Local-Network-Gateways", "Local network gateway"),
    "microsoft.network/connections": ("Connections", "Gateway connection"),
    "microsoft.network/vpngateways": ("Virtual-Network-Gateways", "VPN gateway (vWAN)"),
    "microsoft.network/p2svpngateways": ("Virtual-Network-Gateways", "Point-to-site VPN gateway"),
    "microsoft.network/vpnsites": ("Local-Network-Gateways", "VPN site"),
    "microsoft.network/expressroutecircuits": ("ExpressRoute-Circuits", "ExpressRoute circuit"),
    "microsoft.network/expressrouteports": ("ExpressRoute-Direct", "ExpressRoute Direct"),
    "microsoft.network/expressroutegateways": ("Virtual-Network-Gateways", "ExpressRoute gateway (vWAN)"),
    "microsoft.network/routetables": ("Route-Tables", "Route table"),
    "microsoft.network/routefilters": ("Route-Filters", "Route filter"),
    "microsoft.network/natgateways": ("NAT", "NAT gateway"),
    "microsoft.network/privateendpoints": ("Private-Endpoints", "Private endpoint"),
    "microsoft.network/privatelinkservices": ("Private-Link-Services", "Private Link service"),
    "microsoft.network/privatednszones": ("DNS-Zones", "Private DNS zone"),
    "microsoft.network/privatednszones/virtualnetworklinks": ("DNS-Zones", "Private DNS zone link"),
    "microsoft.network/dnszones": ("DNS-Zones", "DNS zone"),
    "microsoft.network/dnsresolvers": ("DNS-Private-Resolver", "DNS private resolver"),
    "microsoft.network/dnsforwardingrulesets": ("DNS-Private-Resolver", "DNS forwarding ruleset"),
    "microsoft.network/trafficmanagerprofiles": ("Traffic-Manager-Profiles", "Traffic Manager profile"),
    "microsoft.network/networkwatchers": ("Network-Watcher", "Network Watcher"),
    "microsoft.network/networkwatchers/flowlogs": ("Network-Watcher", "Flow log"),
    "microsoft.network/ddosprotectionplans": ("DDoS-Protection-Plans", "DDoS protection plan"),
    "microsoft.network/ipgroups": ("IP-Groups", "IP group"),
    "microsoft.network/virtualwans": ("Virtual-WANs", "Virtual WAN"),
    "microsoft.network/virtualhubs": ("Virtual-WAN-Hub", "Virtual hub"),
    "microsoft.network/virtualhubs/hubvirtualnetworkconnections": ("Virtual-WAN-Hub", "Hub VNet connection"),
    "microsoft.network/virtualrouters": ("Virtual-Router", "Virtual router"),
    "microsoft.network/serviceendpointpolicies": ("Service-Endpoint-Policies", "Service endpoint policy"),
    "microsoft.network/networkmanagers": ("Network-Managers", "Network manager"),
    "microsoft.network/networksecurityperimeters": ("Network-Security-Perimeters", "Network security perimeter"),
    "microsoft.cdn/profiles": ("Front-Door-and-CDN-Profiles", "Front Door / CDN profile"),
    "microsoft.cdn/profiles/afdendpoints": ("Front-Door-and-CDN-Profiles", "Front Door endpoint"),
    "microsoft.cdn/profiles/endpoints": ("CDN-Profiles", "CDN endpoint"),
    "microsoft.cdn/cdnwebapplicationfirewallpolicies": ("Web-Application-Firewall-Policies(WAF)", "CDN WAF policy"),
    "microsoft.classicnetwork/virtualnetworks": ("Virtual-Networks-(Classic)", "Virtual network (classic)"),
    # --- web & apps ------------------------------------------------------
    "microsoft.web/sites": ("App-Services", "App Service"),
    "microsoft.web/sites/slots": ("Web-Slots", "Deployment slot"),
    "microsoft.web/sites/functions": ("Function-Apps", "Function"),
    "microsoft.web/serverfarms": ("App-Service-Plans", "App Service plan"),
    "microsoft.web/staticsites": ("Static-Apps", "Static Web App"),
    "microsoft.web/certificates": ("App-Service-Certificates", "App Service certificate"),
    "microsoft.web/connections": ("API-Connections", "API connection"),
    "microsoft.web/customapis": ("Logic-Apps-Custom-Connector", "Custom connector"),
    "microsoft.web/hostingenvironments": ("App-Service-Environments", "App Service Environment"),
    "microsoft.certificateregistration/certificateorders": ("App-Service-Certificates", "App Service certificate order"),
    "microsoft.domainregistration/domains": ("App-Service-Domains", "App Service domain"),
    "microsoft.apimanagement/service": ("API-Management-Services", "API Management"),
    "microsoft.apimanagement/service/apis": ("API-Proxy", "API"),
    "microsoft.apicenter/services": ("API-Center", "API Center"),
    "microsoft.signalrservice/signalr": ("SignalR", "SignalR"),
    "microsoft.signalrservice/webpubsub": ("SignalR", "Web PubSub"),
    "microsoft.appconfiguration/configurationstores": ("App-Configuration", "App Configuration"),
    "microsoft.notificationhubs/namespaces": ("Notification-Hub-Namespaces", "Notification Hub namespace"),
    "microsoft.notificationhubs/namespaces/notificationhubs": ("Notification-Hubs", "Notification Hub"),
    "microsoft.appplatform/spring": ("Azure-Spring-Apps", "Azure Spring Apps"),
    # --- containers ------------------------------------------------------
    "microsoft.containerservice/managedclusters": ("Kubernetes-Services", "AKS cluster"),
    "microsoft.containerservice/fleets": ("Kubernetes-Fleet-Manager", "Kubernetes fleet"),
    "microsoft.containerregistry/registries": ("Container-Registries", "Container registry"),
    "microsoft.containerinstance/containergroups": ("Container-Instances", "Container instance"),
    "microsoft.app/containerapps": ("Worker-Container-App", "Container app"),
    "microsoft.app/jobs": ("Worker-Container-App", "Container app job"),
    "microsoft.app/managedenvironments": ("Container-Apps-Environments", "Container Apps environment"),
    "microsoft.redhatopenshift/openshiftclusters": ("Azure-Red-Hat-OpenShift", "Azure Red Hat OpenShift"),
    "microsoft.kubernetes/connectedclusters": ("Arc-Kubernetes", "Arc-enabled Kubernetes"),
    "microsoft.servicefabric/clusters": ("Service-Fabric-Clusters", "Service Fabric cluster"),
    "microsoft.servicefabric/managedclusters": ("Managed-Service-Fabric", "Service Fabric managed cluster"),
    # --- integration -----------------------------------------------------
    "microsoft.logic/workflows": ("Logic-Apps", "Logic app"),
    "microsoft.logic/integrationaccounts": ("Integration-Accounts", "Integration account"),
    "microsoft.logic/integrationserviceenvironments": ("Integration-Service-Environments", "Integration service environment"),
    "microsoft.servicebus/namespaces": ("Azure-Service-Bus", "Service Bus namespace"),
    "microsoft.servicebus/namespaces/queues": ("Azure-Service-Bus", "Service Bus queue"),
    "microsoft.servicebus/namespaces/topics": ("Azure-Service-Bus", "Service Bus topic"),
    "microsoft.eventhub/namespaces": ("Event-Hubs", "Event Hubs namespace"),
    "microsoft.eventhub/namespaces/eventhubs": ("Event-Hubs", "Event hub"),
    "microsoft.eventhub/clusters": ("Event-Hub-Clusters", "Event Hubs cluster"),
    "microsoft.eventgrid/topics": ("Event-Grid-Topics", "Event Grid topic"),
    "microsoft.eventgrid/domains": ("Event-Grid-Domains", "Event Grid domain"),
    "microsoft.eventgrid/systemtopics": ("System-Topic", "Event Grid system topic"),
    "microsoft.eventgrid/eventsubscriptions": ("Event-Grid-Subscriptions", "Event Grid subscription"),
    "microsoft.eventgrid/partnernamespaces": ("Partner-Namespace", "Event Grid partner namespace"),
    "microsoft.eventgrid/partnertopics": ("Partner-Topic", "Event Grid partner topic"),
    "microsoft.relay/namespaces": ("Relays", "Relay namespace"),
    "microsoft.communication/communicationservices": ("Azure-Communication-Services", "Communication Services"),
    "microsoft.communication/emailservices": ("Azure-Communication-Services", "Email Communication Service"),
    # --- databases & analytics -------------------------------------------
    "microsoft.sql/servers": ("SQL-Server", "SQL server"),
    "microsoft.sql/servers/databases": ("SQL-Database", "SQL database"),
    "microsoft.sql/servers/elasticpools": ("SQL-Elastic-Pools", "SQL elastic pool"),
    "microsoft.sql/servers/jobagents": ("Elastic-Job-Agents", "Elastic job agent"),
    "microsoft.sql/managedinstances": ("SQL-Managed-Instance", "SQL managed instance"),
    "microsoft.sql/managedinstances/databases": ("Managed-Database", "Managed database"),
    "microsoft.sql/virtualclusters": ("Virtual-Clusters", "SQL virtual cluster"),
    "microsoft.sql/instancepools": ("Instance-Pools", "SQL instance pool"),
    "microsoft.documentdb/databaseaccounts": ("Azure-Cosmos-DB", "Cosmos DB account"),
    "microsoft.documentdb/databaseaccounts/sqldatabases": ("Azure-Cosmos-DB", "Cosmos DB database"),
    "microsoft.documentdb/databaseaccounts/mongodbdatabases": ("Azure-Cosmos-DB", "Cosmos DB Mongo database"),
    "microsoft.documentdb/cassandraclusters": ("Managed-Instance-Apache-Cassandra", "Managed Cassandra cluster"),
    "microsoft.documentdb/mongoclusters": ("Azure-Cosmos-DB", "Cosmos DB for MongoDB vCore"),
    "microsoft.dbforpostgresql/servers": ("Azure-Database-PostgreSQL-Server", "PostgreSQL server"),
    "microsoft.dbforpostgresql/flexibleservers": ("Azure-Database-PostgreSQL-Server", "PostgreSQL flexible server"),
    "microsoft.dbforpostgresql/flexibleservers/databases": ("Azure-Database-PostgreSQL-Server", "PostgreSQL database"),
    "microsoft.dbforpostgresql/servergroupsv2": ("Azure-Database-PostgreSQL-Server-Group", "Cosmos DB for PostgreSQL"),
    "microsoft.dbformysql/servers": ("Azure-Database-MySQL-Server", "MySQL server"),
    "microsoft.dbformysql/flexibleservers": ("Azure-Database-MySQL-Server", "MySQL flexible server"),
    "microsoft.dbformysql/flexibleservers/databases": ("Azure-Database-MySQL-Server", "MySQL database"),
    "microsoft.dbformariadb/servers": ("Azure-Database-MariaDB-Server", "MariaDB server"),
    "microsoft.cache/redis": ("Cache-Redis", "Azure Cache for Redis"),
    "microsoft.cache/redisenterprise": ("Azure-Managed-Redis", "Azure Managed Redis"),
    "microsoft.synapse/workspaces": ("Azure-Synapse-Analytics", "Synapse workspace"),
    "microsoft.synapse/workspaces/sqlpools": ("SQL-Data-Warehouses", "Synapse SQL pool"),
    "microsoft.synapse/workspaces/bigdatapools": ("Azure-Synapse-Analytics", "Synapse Spark pool"),
    "microsoft.databricks/workspaces": ("Azure-Databricks", "Databricks workspace"),
    "microsoft.databricks/accessconnectors": ("Azure-Databricks", "Databricks access connector"),
    "microsoft.datafactory/factories": ("Data-Factories", "Data factory"),
    "microsoft.kusto/clusters": ("Azure-Data-Explorer-Clusters", "Data Explorer cluster"),
    "microsoft.kusto/clusters/databases": ("Azure-Data-Explorer-Clusters", "Data Explorer database"),
    "microsoft.datalakestore/accounts": ("Data-Lake-Store-Gen1", "Data Lake Storage Gen1"),
    "microsoft.datalakeanalytics/accounts": ("Data-Lake-Analytics", "Data Lake Analytics"),
    "microsoft.streamanalytics/streamingjobs": ("Stream-Analytics-Jobs", "Stream Analytics job"),
    "microsoft.hdinsight/clusters": ("HD-Insight-Clusters", "HDInsight cluster"),
    "microsoft.analysisservices/servers": ("Analysis-Services", "Analysis Services"),
    "microsoft.powerbidedicated/capacities": ("Power-BI-Embedded", "Power BI Embedded"),
    "microsoft.purview/accounts": ("Azure-Purview-Accounts", "Purview account"),
    "microsoft.datashare/accounts": ("Data-Shares", "Data Share account"),
    "microsoft.datamigration/services": ("Azure-Database-Migration-Services", "Database Migration Service"),
    "microsoft.datamigration/sqlmigrationservices": ("Azure-Database-Migration-Services", "Database Migration Service"),
    # --- storage & backup ------------------------------------------------
    "microsoft.storage/storageaccounts": ("Storage-Accounts", "Storage account"),
    "microsoft.storage/storageaccounts/blobservices/containers": ("Storage-Container", "Blob container"),
    "microsoft.storage/storageaccounts/fileservices/shares": ("Azure-Fileshares", "File share"),
    "microsoft.storage/storageaccounts/queueservices/queues": ("Storage-Queue", "Storage queue"),
    "microsoft.storage/storageaccounts/tableservices/tables": ("Table", "Storage table"),
    "microsoft.classicstorage/storageaccounts": ("Storage-Accounts-(Classic)", "Storage account (classic)"),
    "microsoft.storagesync/storagesyncservices": ("Storage-Sync-Services", "Storage Sync Service"),
    "microsoft.netapp/netappaccounts": ("Azure-NetApp-Files", "NetApp account"),
    "microsoft.storagecache/caches": ("Azure-HCP-Cache", "HPC cache"),
    "microsoft.elasticsan/elasticsans": ("Elastic-SAN", "Elastic SAN"),
    "microsoft.databox/jobs": ("Data-Box", "Data Box job"),
    "microsoft.storagemover/storagemovers": ("Azure-Storage-Mover", "Storage Mover"),
    "microsoft.recoveryservices/vaults": ("Recovery-Services-Vaults", "Recovery Services vault"),
    "microsoft.recoveryservices/vaults/backupfabrics/protectioncontainers/protecteditems": ("Azure-Backup-Center", "Backup item"),
    "microsoft.dataprotection/backupvaults": ("Backup-Vault", "Backup vault"),
    "microsoft.dataprotection/resourceguards": ("Resource-Guard", "Resource guard"),
    # --- AI --------------------------------------------------------------
    "microsoft.cognitiveservices/accounts": ("Cognitive-Services", "Azure AI services"),
    "microsoft.machinelearningservices/workspaces": ("Machine-Learning", "Machine Learning workspace"),
    "microsoft.search/searchservices": ("Cognitive-Search", "AI Search"),
    "microsoft.botservice/botservices": ("Bot-Services", "Bot service"),
    # --- identity & security ---------------------------------------------
    "microsoft.keyvault/vaults": ("Key-Vaults", "Key vault"),
    "microsoft.keyvault/managedhsms": ("Dedicated-HSM", "Managed HSM"),
    "microsoft.managedidentity/userassignedidentities": ("Managed-Identities", "Managed identity"),
    "microsoft.aad/domainservices": ("Entra-Domain-Services", "Entra Domain Services"),
    "microsoft.azureactivedirectory/b2cdirectories": ("Azure-AD-B2C", "Azure AD B2C"),
    "microsoft.attestation/attestationproviders": ("AzureAttestation", "Attestation provider"),
    "microsoft.confidentialledger/ledgers": ("Confidential-Ledgers", "Confidential ledger"),
    # --- monitoring & management -----------------------------------------
    "microsoft.operationalinsights/workspaces": ("Log-Analytics-Workspaces", "Log Analytics workspace"),
    "microsoft.operationalinsights/querypacks": ("Log-Analytics-Query-Pack", "Log Analytics query pack"),
    "microsoft.operationsmanagement/solutions": ("Solutions", "Log Analytics solution"),
    "microsoft.insights/components": ("Application-Insights", "Application Insights"),
    "microsoft.insights/actiongroups": ("Alerts", "Action group"),
    "microsoft.insights/metricalerts": ("Alerts", "Metric alert"),
    "microsoft.insights/scheduledqueryrules": ("Alerts", "Log alert"),
    "microsoft.insights/activitylogalerts": ("Alerts", "Activity log alert"),
    "microsoft.insights/autoscalesettings": ("Auto-Scale", "Autoscale setting"),
    "microsoft.insights/workbooks": ("Azure-Workbooks", "Workbook"),
    "microsoft.insights/workbooktemplates": ("Azure-Workbooks", "Workbook template"),
    "microsoft.insights/datacollectionrules": ("Data-Collection-Rules", "Data collection rule"),
    "microsoft.insights/datacollectionendpoints": ("Data-Collection-Rules", "Data collection endpoint"),
    "microsoft.insights/webtests": ("Web-Test", "Availability test"),
    "microsoft.insights/privatelinkscopes": ("Private-Link", "Azure Monitor Private Link scope"),
    "microsoft.alertsmanagement/smartdetectoralertrules": ("Alerts", "Smart detector alert rule"),
    "microsoft.alertsmanagement/actionrules": ("Alerts", "Alert processing rule"),
    "microsoft.alertsmanagement/prometheusrulegroups": ("Alerts", "Prometheus rule group"),
    "microsoft.monitor/accounts": ("Monitor", "Azure Monitor workspace"),
    "microsoft.dashboard/grafana": ("Azure-Managed-Grafana", "Managed Grafana"),
    "microsoft.portal/dashboards": ("Dashboard", "Portal dashboard"),
    "microsoft.automation/automationaccounts": ("Automation-Accounts", "Automation account"),
    "microsoft.automation/automationaccounts/runbooks": ("Automation-Accounts", "Runbook"),
    "microsoft.resources/templatespecs": ("Template-Specs", "Template spec"),
    "microsoft.resources/deploymentscripts": ("Templates", "Deployment script"),
    "microsoft.solutions/applications": ("Managed-Applications-Center", "Managed application"),
    "microsoft.devtestlab/labs": ("DevTest-Labs", "DevTest lab"),
    "microsoft.devtestlab/schedules": ("Scheduler", "Auto-shutdown schedule"),
    "microsoft.loadtestservice/loadtests": ("Azure-Load-Testing", "Load test"),
    "microsoft.chaos/experiments": ("Azure-Chaos-Studio", "Chaos experiment"),
    "microsoft.visualstudio/account": ("Azure-DevOps", "Azure DevOps organization"),
    "microsoft.saas/resources": ("Software-as-a-Service", "SaaS resource"),
    # --- IoT -------------------------------------------------------------
    "microsoft.devices/iothubs": ("IoT-Hub", "IoT hub"),
    "microsoft.devices/provisioningservices": ("Device-Provisioning-Services", "Device Provisioning Service"),
    "microsoft.iotcentral/iotapps": ("IoT-Central-Applications", "IoT Central application"),
    "microsoft.digitaltwins/digitaltwinsinstances": ("Digital-Twins", "Digital Twins instance"),
    "microsoft.timeseriesinsights/environments": ("Time-Series-Insights-Environments", "Time Series Insights"),
    "microsoft.maps/accounts": ("Azure-Maps-Accounts", "Maps account"),
    "microsoft.deviceupdate/accounts": ("Device-Update-IoT-Hub", "Device Update account"),
    # --- hybrid & other --------------------------------------------------
    "microsoft.azurearcdata/sqlmanagedinstances": ("Arc-SQL-Managed-Instance", "Arc SQL managed instance"),
    "microsoft.azurearcdata/sqlserverinstances": ("Arc-SQL-Server", "Arc-enabled SQL Server"),
    "microsoft.azurearcdata/datacontrollers": ("Arc-Data-services", "Arc data controller"),
    "microsoft.azurestackhci/clusters": ("Azure-Stack", "Azure Local cluster"),
    "microsoft.media/mediaservices": ("Azure-Media-Service", "Media Services account"),
    "microsoft.healthcareapis/services": ("Azure-API-for-FHIR", "Azure API for FHIR"),
    "microsoft.healthcareapis/workspaces": ("FHIR-Service", "Health Data Services workspace"),
}

# Fallback icon and category per resource provider (lower case).
# provider -> (icon file stem or None for the generic icon, category)
PROVIDERS = {
    "microsoft.compute": (None, "compute"),
    "microsoft.classiccompute": (None, "compute"),
    "microsoft.hybridcompute": ("Azure-Arc", "compute"),
    "microsoft.batch": ("Batch-Accounts", "compute"),
    "microsoft.desktopvirtualization": ("Azure-Virtual-Desktop", "compute"),
    "microsoft.avs": ("Azure-VMware-Solution", "compute"),
    "microsoft.sqlvirtualmachine": ("Azure-SQL-VM", "compute"),
    "microsoft.maintenance": ("Maintenance-Configuration", "compute"),
    "microsoft.virtualmachineimages": ("Image-Templates", "compute"),
    "microsoft.network": (None, "network"),
    "microsoft.classicnetwork": (None, "network"),
    "microsoft.cdn": ("Front-Door-and-CDN-Profiles", "network"),
    "microsoft.web": ("App-Services", "web"),
    "microsoft.certificateregistration": ("App-Service-Certificates", "web"),
    "microsoft.domainregistration": ("App-Service-Domains", "web"),
    "microsoft.apimanagement": ("API-Management-Services", "web"),
    "microsoft.apicenter": ("API-Center", "web"),
    "microsoft.signalrservice": ("SignalR", "web"),
    "microsoft.appconfiguration": ("App-Configuration", "web"),
    "microsoft.notificationhubs": ("Notification-Hubs", "web"),
    "microsoft.appplatform": ("Azure-Spring-Apps", "web"),
    "microsoft.containerservice": ("Kubernetes-Services", "containers"),
    "microsoft.containerregistry": ("Container-Registries", "containers"),
    "microsoft.containerinstance": ("Container-Instances", "containers"),
    "microsoft.app": ("Container-Apps-Environments", "containers"),
    "microsoft.redhatopenshift": ("Azure-Red-Hat-OpenShift", "containers"),
    "microsoft.kubernetes": ("Arc-Kubernetes", "containers"),
    "microsoft.kubernetesconfiguration": ("Arc-Kubernetes", "containers"),
    "microsoft.servicefabric": ("Service-Fabric-Clusters", "containers"),
    "microsoft.logic": ("Logic-Apps", "integration"),
    "microsoft.servicebus": ("Azure-Service-Bus", "integration"),
    "microsoft.eventhub": ("Event-Hubs", "integration"),
    "microsoft.eventgrid": ("Event-Grid-Topics", "integration"),
    "microsoft.relay": ("Relays", "integration"),
    "microsoft.communication": ("Azure-Communication-Services", "integration"),
    "microsoft.sql": ("Azure-SQL", "data"),
    "microsoft.documentdb": ("Azure-Cosmos-DB", "data"),
    "microsoft.dbforpostgresql": ("Azure-Database-PostgreSQL-Server", "data"),
    "microsoft.dbformysql": ("Azure-Database-MySQL-Server", "data"),
    "microsoft.dbformariadb": ("Azure-Database-MariaDB-Server", "data"),
    "microsoft.cache": ("Cache-Redis", "data"),
    "microsoft.synapse": ("Azure-Synapse-Analytics", "data"),
    "microsoft.databricks": ("Azure-Databricks", "data"),
    "microsoft.datafactory": ("Data-Factories", "data"),
    "microsoft.kusto": ("Azure-Data-Explorer-Clusters", "data"),
    "microsoft.datalakestore": ("Data-Lake-Store-Gen1", "data"),
    "microsoft.datalakeanalytics": ("Data-Lake-Analytics", "data"),
    "microsoft.streamanalytics": ("Stream-Analytics-Jobs", "data"),
    "microsoft.hdinsight": ("HD-Insight-Clusters", "data"),
    "microsoft.analysisservices": ("Analysis-Services", "data"),
    "microsoft.powerbidedicated": ("Power-BI-Embedded", "data"),
    "microsoft.purview": ("Azure-Purview-Accounts", "data"),
    "microsoft.datashare": ("Data-Shares", "data"),
    "microsoft.datamigration": ("Azure-Database-Migration-Services", "data"),
    "microsoft.storage": ("Storage-Accounts", "storage"),
    "microsoft.classicstorage": ("Storage-Accounts-(Classic)", "storage"),
    "microsoft.storagesync": ("Storage-Sync-Services", "storage"),
    "microsoft.netapp": ("Azure-NetApp-Files", "storage"),
    "microsoft.storagecache": ("Azure-HCP-Cache", "storage"),
    "microsoft.elasticsan": ("Elastic-SAN", "storage"),
    "microsoft.databox": ("Data-Box", "storage"),
    "microsoft.storagemover": ("Azure-Storage-Mover", "storage"),
    "microsoft.recoveryservices": ("Recovery-Services-Vaults", "storage"),
    "microsoft.dataprotection": ("Backup-Vault", "storage"),
    "microsoft.cognitiveservices": ("Cognitive-Services", "ai"),
    "microsoft.machinelearningservices": ("Machine-Learning", "ai"),
    "microsoft.search": ("Cognitive-Search", "ai"),
    "microsoft.botservice": ("Bot-Services", "ai"),
    "microsoft.keyvault": ("Key-Vaults", "security"),
    "microsoft.managedidentity": ("Managed-Identities", "security"),
    "microsoft.aad": ("Entra-Domain-Services", "security"),
    "microsoft.azureactivedirectory": ("Azure-AD-B2C", "security"),
    "microsoft.security": ("Microsoft-Defender-for-Cloud", "security"),
    "microsoft.securityinsights": ("Azure-Sentinel", "security"),
    "microsoft.attestation": ("AzureAttestation", "security"),
    "microsoft.confidentialledger": ("Confidential-Ledgers", "security"),
    "microsoft.authorization": ("Policy", "security"),
    "microsoft.operationalinsights": ("Log-Analytics-Workspaces", "monitoring"),
    "microsoft.operationsmanagement": ("Solutions", "monitoring"),
    "microsoft.insights": ("Monitor", "monitoring"),
    "microsoft.alertsmanagement": ("Alerts", "monitoring"),
    "microsoft.monitor": ("Monitor", "monitoring"),
    "microsoft.dashboard": ("Azure-Managed-Grafana", "monitoring"),
    "microsoft.portal": ("Dashboard", "monitoring"),
    "microsoft.automation": ("Automation-Accounts", "management"),
    "microsoft.resources": ("Templates", "management"),
    "microsoft.solutions": ("Managed-Applications-Center", "management"),
    "microsoft.managedservices": ("Azure-Lighthouse", "management"),
    "microsoft.migrate": ("Azure-Migrate", "management"),
    "microsoft.offazure": ("Azure-Migrate", "management"),
    "microsoft.devtestlab": ("DevTest-Labs", "management"),
    "microsoft.labservices": ("Lab-Services", "management"),
    "microsoft.devcenter": ("Microsoft-Dev-Box", "management"),
    "microsoft.loadtestservice": ("Azure-Load-Testing", "management"),
    "microsoft.chaos": ("Azure-Chaos-Studio", "management"),
    "microsoft.costmanagement": ("Cost-Management", "management"),
    "microsoft.visualstudio": ("Azure-DevOps", "management"),
    "microsoft.devices": ("IoT-Hub", "iot"),
    "microsoft.iotcentral": ("IoT-Central-Applications", "iot"),
    "microsoft.iotoperations": ("Azure-IoT-Operations", "iot"),
    "microsoft.digitaltwins": ("Digital-Twins", "iot"),
    "microsoft.timeseriesinsights": ("Time-Series-Insights-Environments", "iot"),
    "microsoft.maps": ("Azure-Maps-Accounts", "iot"),
    "microsoft.deviceupdate": ("Device-Update-IoT-Hub", "iot"),
    "microsoft.azurearcdata": ("Arc-Data-services", "data"),
    "microsoft.azurestackhci": ("Azure-Stack", "compute"),
    "microsoft.media": ("Azure-Media-Service", "other"),
    "microsoft.healthcareapis": ("FHIR-Service", "data"),
    "microsoft.orbital": ("Azure-Orbital", "other"),
    "microsoft.sendgrid": ("SendGrid-Accounts", "integration"),
}

# Order in which categories are laid out inside a resource group.
CATEGORY_ORDER = ["network", "compute", "containers", "web", "integration", "data", "storage",
                  "ai", "iot", "security", "monitoring", "management", "other"]

# Azure AI services accounts are told apart by their kind.
_COGNITIVE_KINDS = {
    "openai": ("Azure-OpenAI", "Azure OpenAI"),
    "aiservices": ("AI-Studio", "Azure AI services"),
    "speechservices": ("Speech-Services", "Speech service"),
    "computervision": ("Computer-Vision", "Computer Vision"),
    "formrecognizer": ("Form-Recognizers", "Document Intelligence"),
    "texttranslation": ("Translator-Text", "Translator"),
    "contentsafety": ("Content-Safety", "Content Safety"),
    "face": ("Face-APIs", "Face API"),
    "textanalytics": ("Language", "Language service"),
    "luis": ("Language-Understanding", "Language Understanding"),
    "customvision.training": ("Custom-Vision", "Custom Vision"),
    "customvision.prediction": ("Custom-Vision", "Custom Vision"),
}


def describe(resource_type, kind="", sku_name=""):
    """Return ``(icon file stem, display name)`` for a resource."""
    type_lower = (resource_type or "").lower()
    kind_lower = (kind or "").lower()
    if type_lower == "microsoft.web/sites":
        if "workflowapp" in kind_lower:
            return "Logic-Apps", "Logic app (Standard)"
        if "functionapp" in kind_lower:
            return "Function-Apps", "Function app"
    elif type_lower == "microsoft.cognitiveservices/accounts" and kind_lower in _COGNITIVE_KINDS:
        return _COGNITIVE_KINDS[kind_lower]
    elif type_lower == "microsoft.machinelearningservices/workspaces" and kind_lower in ("hub", "project"):
        return "AI-Studio", f"Azure AI Foundry {kind_lower}"
    elif type_lower == "microsoft.cdn/profiles" and sku_name:
        if "frontdoor" in sku_name.lower():
            return "Front-Door-and-CDN-Profiles", "Front Door profile"
        return "CDN-Profiles", "CDN profile"

    if type_lower in RESOURCE_TYPES:
        return RESOURCE_TYPES[type_lower]
    provider_icon = PROVIDERS.get(type_lower.split("/")[0], (None, "other"))[0]
    return provider_icon or DEFAULT_ICON, _name_from_type(resource_type)


def icon_for(resource_type, kind="", sku_name=""):
    return describe(resource_type, kind, sku_name)[0]


def friendly_type(resource_type, kind="", sku_name=""):
    return describe(resource_type, kind, sku_name)[1]


def category_of(resource_type):
    """Coarse category of a resource type, used for ordering and colours."""
    return PROVIDERS.get((resource_type or "").lower().split("/")[0], (None, "other"))[1]


def _name_from_type(resource_type):
    """'Microsoft.Foo/barBazes' -> 'Bar baze'-ish readable name for unknown types."""
    last = (resource_type or "").rsplit("/", 1)[-1]
    words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", last).split()
    if not words:
        return resource_type or "Resource"
    word = words[-1]
    lower = word.lower()
    if lower.endswith("ies"):
        word = word[:-3] + "y"
    elif lower.endswith(("sses", "xes", "ches", "shes")):
        word = word[:-2]
    elif lower.endswith("s") and not lower.endswith(("ss", "us", "is")):
        word = word[:-1]
    words[-1] = word
    # Sentence case, but leave acronyms such as "IP" or "SQL" alone.
    words = [w.lower() if w[1:].islower() else w for w in words]
    text = " ".join(words)
    return text[:1].upper() + text[1:]


def icon_dir():
    """Folder holding the Azure SVG icons (also when frozen with PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "icons")


def icon_path(stem):
    """Path of an icon file; falls back to the generic icon when it is missing."""
    path = os.path.join(icon_dir(), f"{stem}.svg")
    if not os.path.exists(path):
        path = os.path.join(icon_dir(), f"{DEFAULT_ICON}.svg")
    return path


@functools.lru_cache(maxsize=None)
def icon_data_uri(stem):
    """The icon as a draw.io style data URI (``data:image/svg+xml,<base64>``).

    draw.io leaves out ``;base64`` because ';' separates style entries.
    Returns '' when the icon file cannot be read.
    """
    try:
        with open(icon_path(stem), "rb") as handle:
            return "data:image/svg+xml," + base64.b64encode(handle.read()).decode("ascii")
    except OSError:
        return ""


def drawio_image(stem, mode="embedded", size=48):
    """``(image, width, height)`` for the image styles of a draw.io shape.

    ``library`` points at the Azure icons that ship with draw.io where there
    is one; icons draw.io does not have are embedded either way. draw.io's own
    icons are not square, so they are fitted into ``size`` keeping their shape.
    """
    if mode == "library" and stem in LIBRARY_ICONS:
        path, width, height = LIBRARY_ICONS[stem]
        scale = size / max(width, height)
        return LIBRARY_PREFIX + path, round(width * scale), round(height * scale)
    return icon_data_uri(stem), size, size
