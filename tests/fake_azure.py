"""A small fake of the Azure Resource Manager API serving a synthetic tenant.

It lets the whole tool run end-to-end without Azure credentials: the test
suite and the files in ``example output/`` are produced against it. The tenant
("Contoso") is deliberately shaped like a real hub-and-spoke environment so the
diagrams have something realistic to show.
"""
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

SUB_PROD = "11111111-1111-1111-1111-111111111111"
SUB_DEV = "22222222-2222-2222-2222-222222222222"
TENANT_ID = "99999999-9999-9999-9999-999999999999"
TOKEN = "fake-token"


class FakeCredential:
    """Stands in for an azure-identity credential."""

    def get_token(self, *scopes, **kwargs):  # noqa: ARG002
        from azure.core.credentials import AccessToken
        return AccessToken(TOKEN, int(time.time()) + 3600)


class Tenant:
    """Synthetic tenant: subscriptions, resource groups, resources, children."""

    def __init__(self):
        self.subscriptions = []
        self.groups = {}            # subscription id -> [resource group dict]
        self.resources = []         # raw ARM resources (with properties)
        self.children = {}          # "<parent id>/<path>" lower -> [raw child]
        self.recommendations = {}   # subscription id -> [raw recommendation]
        self.graph_hidden_types = set()   # lower types Resource Graph "does not index"
        self.api_overrides = {}     # lower type -> versions the GET endpoint really accepts

    def subscription(self, subscription_id, name):
        self.subscriptions.append({
            "id": f"/subscriptions/{subscription_id}", "subscriptionId": subscription_id,
            "displayName": name, "state": "Enabled", "tenantId": TENANT_ID,
        })
        self.groups[subscription_id] = []
        self.recommendations[subscription_id] = []

    def group(self, subscription_id, name, location="westeurope", tags=None):
        self.groups[subscription_id].append({
            "id": f"/subscriptions/{subscription_id}/resourceGroups/{name}", "name": name,
            "type": "Microsoft.Resources/resourceGroups", "location": location,
            "tags": tags or {}, "properties": {"provisioningState": "Succeeded"},
        })

    def add(self, subscription_id, group, resource_type, name, properties=None, location="westeurope", **extra):
        """Add a resource and return its id. ``name`` may be 'parent/child'."""
        namespace, *types = resource_type.split("/")
        names = name.split("/")
        path = "/".join(f"{t}/{n}" for t, n in zip(types, names))
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{group}/providers/{namespace}/{path}"
        resource = {"id": resource_id, "name": name, "type": resource_type, "location": location}
        resource.update({key: value for key, value in extra.items() if value is not None})
        resource["properties"] = {"provisioningState": "Succeeded", **(properties or {})}
        self.resources.append(resource)
        return resource_id

    def child(self, parent_id, path, child_type, name, properties=None):
        child_id = f"{parent_id}/{path}/{name}"
        self.children.setdefault(f"{parent_id}/{path}".lower(), []).append({
            "id": child_id, "name": name, "type": child_type, "properties": properties or {},
        })
        return child_id

    def recommend(self, subscription_id, resource_id, category, impact, problem, solution):
        number = len(self.recommendations[subscription_id]) + 1
        guid = f"00000000-0000-0000-0000-{number:012d}"
        self.recommendations[subscription_id].append({
            "id": f"{resource_id}/providers/Microsoft.Advisor/recommendations/{guid}", "name": guid,
            "type": "Microsoft.Advisor/recommendations",
            "properties": {
                "category": category, "impact": impact,
                "impactedField": "/".join(resource_id.split("/providers/")[-1].split("/")[0:2]),
                "impactedValue": resource_id.rsplit("/", 1)[-1],
                "shortDescription": {"problem": problem, "solution": solution},
                "resourceMetadata": {"resourceId": resource_id},
            },
        })


def _ref(resource_id):
    return {"id": resource_id}


def _subnet(vnet_id, name, prefix, nsg=None, route_table=None, nat=None, delegation=None):
    properties = {"addressPrefix": prefix, "provisioningState": "Succeeded",
                  "privateEndpointNetworkPolicies": "Disabled"}
    if nsg:
        properties["networkSecurityGroup"] = _ref(nsg)
    if route_table:
        properties["routeTable"] = _ref(route_table)
    if nat:
        properties["natGateway"] = _ref(nat)
    if delegation:
        properties["delegations"] = [{"name": "delegation", "properties": {"serviceName": delegation}}]
    return {"id": f"{vnet_id}/subnets/{name}", "name": name,
            "type": "Microsoft.Network/virtualNetworks/subnets", "properties": properties}


def _peering(vnet_id, name, remote_id, gateway_transit=False, use_remote_gateways=False):
    return {"id": f"{vnet_id}/virtualNetworkPeerings/{name}", "name": name,
            "type": "Microsoft.Network/virtualNetworks/virtualNetworkPeerings",
            "properties": {"peeringState": "Connected", "remoteVirtualNetwork": _ref(remote_id),
                           "allowVirtualNetworkAccess": True, "allowForwardedTraffic": True,
                           "allowGatewayTransit": gateway_transit, "useRemoteGateways": use_remote_gateways}}


def build_tenant():  # noqa: PLR0915 - one long, flat description of the tenant
    t = Tenant()
    t.subscription(SUB_PROD, "Contoso Production")
    t.subscription(SUB_DEV, "Contoso Dev/Test")
    P, D = SUB_PROD, SUB_DEV

    for name, tags in [("rg-network-hub", {"env": "prod", "owner": "network-team"}),
                       ("rg-app-prod", {"env": "prod", "owner": "app-team"}),
                       ("rg-data-prod", {"env": "prod", "owner": "data-team"}),
                       ("rg-monitoring", {"env": "prod", "owner": "ops"}),
                       ("MC_rg-app-prod_aks-prod_westeurope", {"env": "prod"}),
                       ("rg-research", {"env": "lab"}),
                       ("rg-sandbox-empty", {})]:
        t.group(P, name, tags=tags)
    for name in ("rg-dev", "NetworkWatcherRG"):
        t.group(D, name, tags={"env": "dev"} if name == "rg-dev" else {})

    net = "Microsoft.Network"
    hub = f"/subscriptions/{P}/resourceGroups/rg-network-hub/providers/{net}/virtualNetworks/vnet-hub"
    spoke = f"/subscriptions/{P}/resourceGroups/rg-app-prod/providers/{net}/virtualNetworks/vnet-app-prod"
    dev = f"/subscriptions/{D}/resourceGroups/rg-dev/providers/{net}/virtualNetworks/vnet-dev"

    # ---- monitoring (referenced by many others) --------------------------
    law = t.add(P, "rg-monitoring", "Microsoft.OperationalInsights/workspaces", "law-contoso-prod",
                {"customerId": "5f0c2b1e-0000-4000-8000-000000000001", "sku": {"name": "PerGB2018"},
                 "retentionInDays": 90}, tags={"env": "prod"})
    ag_ops = t.add(P, "rg-monitoring", "Microsoft.Insights/actionGroups", "ag-ops-oncall",
                   {"groupShortName": "ops", "enabled": True,
                    "emailReceivers": [{"name": "ops", "emailAddress": "ops@contoso.example"}]}, location="Global")
    t.add(P, "rg-monitoring", "Microsoft.Insights/dataCollectionRules", "dcr-vm-insights",
          {"destinations": {"logAnalytics": [{"workspaceResourceId": law, "name": "law"}]},
           "dataFlows": [{"streams": ["Microsoft-InsightsMetrics"], "destinations": ["law"]}]})
    t.add(P, "rg-monitoring", "Microsoft.Automation/automationAccounts", "aa-contoso-ops",
          {"sku": {"name": "Basic"}, "state": "Ok"}, identity={"type": "SystemAssigned"})
    t.add(P, "rg-monitoring", "Microsoft.Insights/workbooks", "b2c7a6f0-1111-4222-8333-444455556666",
          {"displayName": "Platform overview", "category": "workbook", "sourceId": law}, kind="shared")
    rsv = t.add(P, "rg-monitoring", "Microsoft.RecoveryServices/vaults", "rsv-contoso-prod",
                {"publicNetworkAccess": "Enabled"}, sku={"name": "RS0", "tier": "Standard"})

    # ---- hub network ----------------------------------------------------
    nsg_shared = t.add(P, "rg-network-hub", f"{net}/networkSecurityGroups", "nsg-shared-services",
                       {"securityRules": [{"name": "AllowRdpFromBastion", "properties": {
                           "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp",
                           "sourceAddressPrefix": "10.0.2.0/26", "destinationPortRange": "3389"}}],
                        "subnets": [_ref(f"{hub}/subnets/snet-shared-services")]})
    rt_spokes = t.add(P, "rg-network-hub", f"{net}/routeTables", "rt-spokes-via-firewall",
                      {"disableBgpRoutePropagation": True,
                       "routes": [{"name": "default", "properties": {
                           "addressPrefix": "0.0.0.0/0", "nextHopType": "VirtualAppliance",
                           "nextHopIpAddress": "10.0.1.4"}}],
                       "subnets": [_ref(f"{spoke}/subnets/snet-web"), _ref(f"{spoke}/subnets/snet-aks")]})
    t.add(P, "rg-network-hub", f"{net}/virtualNetworks", "vnet-hub", {
        "addressSpace": {"addressPrefixes": ["10.0.0.0/16"]},
        "dhcpOptions": {"dnsServers": ["10.0.10.4"]},
        "subnets": [
            _subnet(hub, "GatewaySubnet", "10.0.0.0/27"),
            _subnet(hub, "AzureFirewallSubnet", "10.0.1.0/26"),
            _subnet(hub, "AzureBastionSubnet", "10.0.2.0/26"),
            _subnet(hub, "snet-shared-services", "10.0.10.0/24", nsg=nsg_shared),
        ],
        "virtualNetworkPeerings": [
            _peering(hub, "hub-to-app-prod", spoke, gateway_transit=True),
            _peering(hub, "hub-to-dev", dev, gateway_transit=True),
            _peering(hub, "hub-to-partner", f"/subscriptions/33333333-3333-3333-3333-333333333333/resourceGroups/"
                                            f"rg-partner/providers/{net}/virtualNetworks/vnet-partner-shared"),
        ]}, tags={"env": "prod", "role": "hub"})

    def public_ip(sub, group, name, address, attached_to=None):
        properties = {"ipAddress": address, "publicIPAllocationMethod": "Static", "publicIPAddressVersion": "IPv4"}
        if attached_to:
            properties["ipConfiguration"] = _ref(attached_to)
        return t.add(sub, group, f"{net}/publicIPAddresses", name, properties,
                     sku={"name": "Standard", "tier": "Regional"}, zones=["1", "2", "3"])

    hub_rg = f"/subscriptions/{P}/resourceGroups/rg-network-hub/providers/{net}"
    afw_policy = t.add(P, "rg-network-hub", f"{net}/firewallPolicies", "afwp-hub",
                       {"threatIntelMode": "Alert", "sku": {"tier": "Standard"}})
    pip_afw = public_ip(P, "rg-network-hub", "pip-afw-hub", "20.50.10.4",
                        f"{hub_rg}/azureFirewalls/afw-hub/azureFirewallIpConfigurations/ipconfig")
    t.add(P, "rg-network-hub", f"{net}/azureFirewalls", "afw-hub", {
        "sku": {"name": "AZFW_VNet", "tier": "Standard"}, "firewallPolicy": _ref(afw_policy),
        "ipConfigurations": [{"name": "ipconfig", "properties": {
            "privateIPAddress": "10.0.1.4", "subnet": _ref(f"{hub}/subnets/AzureFirewallSubnet"),
            "publicIPAddress": _ref(pip_afw)}}]}, zones=["1", "2", "3"])
    pip_bastion = public_ip(P, "rg-network-hub", "pip-bas-hub", "20.50.10.20",
                            f"{hub_rg}/bastionHosts/bas-hub/bastionHostIpConfigurations/ipconfig")
    t.add(P, "rg-network-hub", f"{net}/bastionHosts", "bas-hub", {
        "dnsName": "bst-0001.bastion.azure.com", "scaleUnits": 2,
        "ipConfigurations": [{"name": "ipconfig", "properties": {
            "subnet": _ref(f"{hub}/subnets/AzureBastionSubnet"), "publicIPAddress": _ref(pip_bastion)}}]},
        sku={"name": "Standard"})
    pip_vgw = public_ip(P, "rg-network-hub", "pip-vgw-hub", "20.50.10.30",
                        f"{hub_rg}/virtualNetworkGateways/vgw-hub/ipConfigurations/default")
    vgw = t.add(P, "rg-network-hub", f"{net}/virtualNetworkGateways", "vgw-hub", {
        "gatewayType": "Vpn", "vpnType": "RouteBased", "sku": {"name": "VpnGw2AZ", "tier": "VpnGw2AZ"},
        "ipConfigurations": [{"name": "default", "properties": {
            "subnet": _ref(f"{hub}/subnets/GatewaySubnet"), "publicIPAddress": _ref(pip_vgw)}}]})
    lgw = t.add(P, "rg-network-hub", f"{net}/localNetworkGateways", "lgw-onprem-brussels",
                {"gatewayIpAddress": "203.0.113.10",
                 "localNetworkAddressSpace": {"addressPrefixes": ["192.168.0.0/16"]}})
    t.add(P, "rg-network-hub", f"{net}/connections", "cn-hub-to-brussels",
          {"connectionType": "IPsec", "connectionStatus": "Connected",
           "virtualNetworkGateway1": _ref(vgw), "localNetworkGateway2": _ref(lgw)})
    for zone in ("privatelink.database.windows.net", "privatelink.blob.core.windows.net",
                 "privatelink.vaultcore.azure.net"):
        t.add(P, "rg-network-hub", f"{net}/privateDnsZones", zone,
              {"numberOfRecordSets": 3, "numberOfVirtualNetworkLinks": 2}, location="global")
        for link_name, vnet_id in (("link-hub", hub), ("link-app-prod", spoke)):
            t.add(P, "rg-network-hub", f"{net}/privateDnsZones/virtualNetworkLinks", f"{zone}/{link_name}",
                  {"virtualNetwork": _ref(vnet_id), "registrationEnabled": False,
                   "virtualNetworkLinkState": "Completed"}, location="global")

    def virtual_machine(sub, group, name, subnet_id, ip, size="Standard_D4s_v5", os_type="Windows",
                        nsg=None, public=None, avset=None, data_disks=0, lb_pool=None, zones=None, tags=None):
        base = f"/subscriptions/{sub}/resourceGroups/{group}/providers"
        vm_id = f"{base}/Microsoft.Compute/virtualMachines/{name}"
        nic_id = f"{base}/{net}/networkInterfaces/{name}-nic"
        ip_config = {"privateIPAddress": ip, "privateIPAllocationMethod": "Dynamic", "primary": True,
                     "subnet": _ref(subnet_id)}
        if public:
            ip_config["publicIPAddress"] = _ref(public_ip(sub, group, f"{name}-pip", public,
                                                          f"{nic_id}/ipConfigurations/ipconfig1"))
        if lb_pool:
            ip_config["loadBalancerBackendAddressPools"] = [_ref(lb_pool)]
        nic_properties = {"ipConfigurations": [{"id": f"{nic_id}/ipConfigurations/ipconfig1", "name": "ipconfig1",
                                                "properties": ip_config}],
                          "virtualMachine": _ref(vm_id), "enableAcceleratedNetworking": True}
        if nsg:
            nic_properties["networkSecurityGroup"] = _ref(nsg)
        t.add(sub, group, f"{net}/networkInterfaces", f"{name}-nic", nic_properties)
        disks = [t.add(sub, group, "Microsoft.Compute/disks", f"{name}-osdisk",
                       {"diskSizeGB": 128, "diskState": "Attached", "osType": os_type},
                       sku={"name": "Premium_LRS", "tier": "Premium"}, managedBy=vm_id)]
        for lun in range(data_disks):
            disks.append(t.add(sub, group, "Microsoft.Compute/disks", f"{name}-datadisk-{lun}",
                               {"diskSizeGB": 512, "diskState": "Attached"},
                               sku={"name": "Premium_LRS", "tier": "Premium"}, managedBy=vm_id))
        properties = {
            "vmId": f"0a1b2c3d-{abs(hash(name)) % 10**4:04d}-4000-8000-000000000000",
            "hardwareProfile": {"vmSize": size},
            "storageProfile": {
                "osDisk": {"osType": os_type, "name": f"{name}-osdisk", "createOption": "FromImage",
                           "managedDisk": {"id": disks[0], "storageAccountType": "Premium_LRS"}},
                "dataDisks": [{"lun": lun, "name": f"{name}-datadisk-{lun}", "managedDisk": _ref(disk)}
                              for lun, disk in enumerate(disks[1:])]},
            "osProfile": {"computerName": name, "adminUsername": "azureadmin"},
            "networkProfile": {"networkInterfaces": [{"id": nic_id, "properties": {"primary": True}}]},
        }
        if avset:
            properties["availabilitySet"] = _ref(avset)
        t.add(sub, group, "Microsoft.Compute/virtualMachines", name, properties, zones=zones, tags=tags,
              identity={"type": "SystemAssigned", "principalId": "aaaa0000-0000-4000-8000-000000000001"})
        t.add(sub, group, "Microsoft.Compute/virtualMachines/extensions", f"{name}/AzureMonitorAgent",
              {"publisher": "Microsoft.Azure.Monitor", "type": "AzureMonitorWindowsAgent"
               if os_type == "Windows" else "AzureMonitorLinuxAgent", "typeHandlerVersion": "1.22"})
        return vm_id

    vm_dc = virtual_machine(P, "rg-network-hub", "vm-dc-01", f"{hub}/subnets/snet-shared-services", "10.0.10.4",
                            size="Standard_D2s_v5", zones=["1"], tags={"role": "domain-controller"})

    # ---- application spoke ----------------------------------------------
    nsg_web = t.add(P, "rg-app-prod", f"{net}/networkSecurityGroups", "nsg-web",
                    {"securityRules": [{"name": "AllowHttpsFromAppGw", "properties": {
                        "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp",
                        "sourceAddressPrefix": "10.1.0.0/24", "destinationPortRange": "443"}}],
                     "subnets": [_ref(f"{spoke}/subnets/snet-web")]})
    nat = t.add(P, "rg-app-prod", f"{net}/natGateways", "ng-app-prod", {"idleTimeoutInMinutes": 4},
                sku={"name": "Standard"})
    t.add(P, "rg-app-prod", f"{net}/virtualNetworks", "vnet-app-prod", {
        "addressSpace": {"addressPrefixes": ["10.1.0.0/16"]},
        "subnets": [
            _subnet(spoke, "snet-appgw", "10.1.0.0/24"),
            _subnet(spoke, "snet-web", "10.1.1.0/24", nsg=nsg_web, route_table=rt_spokes),
            _subnet(spoke, "snet-integration", "10.1.2.0/24", nat=nat, delegation="Microsoft.Web/serverFarms"),
            _subnet(spoke, "snet-private-endpoints", "10.1.3.0/24"),
            _subnet(spoke, "snet-aks", "10.1.16.0/20", route_table=rt_spokes),
            _subnet(spoke, "snet-container-apps", "10.1.32.0/23", delegation="Microsoft.App/environments"),
        ],
        "virtualNetworkPeerings": [_peering(spoke, "app-prod-to-hub", hub, use_remote_gateways=True)],
    }, tags={"env": "prod", "role": "spoke"})

    app_net = f"/subscriptions/{P}/resourceGroups/rg-app-prod/providers/{net}"
    waf = t.add(P, "rg-app-prod", f"{net}/ApplicationGatewayWebApplicationFirewallPolicies", "waf-agw-prod",
                {"policySettings": {"state": "Enabled", "mode": "Prevention"},
                 "managedRules": {"managedRuleSets": [{"ruleSetType": "OWASP", "ruleSetVersion": "3.2"}]}})
    pip_agw = public_ip(P, "rg-app-prod", "pip-agw-prod", "20.50.20.4",
                        f"{app_net}/applicationGateways/agw-prod/frontendIPConfigurations/public")
    t.add(P, "rg-app-prod", f"{net}/applicationGateways", "agw-prod", {
        "sku": {"name": "WAF_v2", "tier": "WAF_v2", "capacity": 2}, "firewallPolicy": _ref(waf),
        "gatewayIPConfigurations": [{"name": "gw", "properties": {"subnet": _ref(f"{spoke}/subnets/snet-appgw")}}],
        "frontendIPConfigurations": [{"name": "public", "properties": {"publicIPAddress": _ref(pip_agw)}}],
        "backendAddressPools": [{"name": "portal", "properties": {
            "backendAddresses": [{"fqdn": "app-contoso-portal.azurewebsites.net"}]}}]}, zones=["1", "2", "3"])

    lb_id = f"{app_net}/loadBalancers/lbi-web"
    lb_pool = f"{lb_id}/backendAddressPools/web"
    avset = t.add(P, "rg-app-prod", "Microsoft.Compute/availabilitySets", "avail-web",
                  {"platformFaultDomainCount": 2, "platformUpdateDomainCount": 5}, sku={"name": "Aligned"})
    vm_web = [virtual_machine(P, "rg-app-prod", f"vm-web-0{n}", f"{spoke}/subnets/snet-web", f"10.1.1.{3 + n}",
                              avset=avset, data_disks=1 if n == 1 else 0, lb_pool=lb_pool,
                              tags={"role": "web", "env": "prod"}) for n in (1, 2)]
    t.add(P, "rg-app-prod", f"{net}/loadBalancers", "lbi-web", {
        "frontendIPConfigurations": [{"id": f"{lb_id}/frontendIPConfigurations/internal", "name": "internal",
                                      "properties": {"privateIPAddress": "10.1.1.100",
                                                     "subnet": _ref(f"{spoke}/subnets/snet-web")}}],
        "backendAddressPools": [{"id": lb_pool, "name": "web", "properties": {"backendIPConfigurations": [
            _ref(f"{app_net}/networkInterfaces/vm-web-0{n}-nic/ipConfigurations/ipconfig1") for n in (1, 2)]}}],
    }, sku={"name": "Standard", "tier": "Regional"})

    uami = t.add(P, "rg-app-prod", "Microsoft.ManagedIdentity/userAssignedIdentities", "id-app-prod",
                 {"principalId": "bbbb0000-0000-4000-8000-000000000001",
                  "clientId": "bbbb0000-0000-4000-8000-000000000002", "tenantId": TENANT_ID})
    appi = t.add(P, "rg-app-prod", "Microsoft.Insights/components", "appi-contoso-prod",
                 {"Application_Type": "web", "IngestionMode": "LogAnalytics", "WorkspaceResourceId": law},
                 kind="web")
    ag_smart = t.add(P, "rg-app-prod", "Microsoft.Insights/actionGroups", "Application Insights Smart Detection",
                     {"groupShortName": "SmartDetect", "enabled": True}, location="Global")
    t.add(P, "rg-app-prod", "Microsoft.AlertsManagement/smartDetectorAlertRules",
          "Failure Anomalies - appi-contoso-prod",
          {"state": "Enabled", "severity": "Sev3", "frequency": "PT1M",
           "detector": {"id": "FailureAnomaliesDetector"}, "scope": [appi],
           "actionGroups": {"groupIds": [ag_smart]}}, location="global")
    t.add(P, "rg-app-prod", "Microsoft.Insights/metricAlerts", "alert-cpu-vm-web-01",
          {"severity": 2, "enabled": True, "scopes": [vm_web[0]], "evaluationFrequency": "PT5M",
           "actions": [{"actionGroupId": ag_ops}],
           "criteria": {"allOf": [{"metricName": "Percentage CPU", "operator": "GreaterThan", "threshold": 80}]}},
          location="global")

    plan = t.add(P, "rg-app-prod", "Microsoft.Web/serverFarms", "asp-contoso-prod",
                 {"numberOfSites": 2, "zoneRedundant": True, "reserved": True},
                 sku={"name": "P1v3", "tier": "PremiumV3", "capacity": 3}, kind="linux")
    identity = {"type": "UserAssigned", "userAssignedIdentities": {uami: {
        "principalId": "bbbb0000-0000-4000-8000-000000000001", "clientId": "bbbb0000-0000-4000-8000-000000000002"}}}
    site_common = {"serverFarmId": plan, "httpsOnly": True, "state": "Running",
                   "virtualNetworkSubnetId": f"{spoke}/subnets/snet-integration"}
    t.add(P, "rg-app-prod", "Microsoft.Web/sites", "app-contoso-portal",
          {**site_common, "defaultHostName": "app-contoso-portal.azurewebsites.net"}, kind="app,linux",
          identity=identity, tags={"env": "prod", "hidden-link: /app-insights-resource-id": appi})
    func = t.add(P, "rg-app-prod", "Microsoft.Web/sites", "func-contoso-orders",
                 {**site_common, "defaultHostName": "func-contoso-orders.azurewebsites.net"},
                 kind="functionapp,linux", identity=identity, tags={"env": "prod"})
    for name in ("ProcessOrder", "SendInvoice"):
        t.child(func, "functions", "Microsoft.Web/sites/functions", name,
                {"language": "dotnet-isolated", "isDisabled": False,
                 "invoke_url_template": f"https://func-contoso-orders.azurewebsites.net/api/{name.lower()}"})

    acr = t.add(P, "rg-app-prod", "Microsoft.ContainerRegistry/registries", "acrcontosoprod",
                {"loginServer": "acrcontosoprod.azurecr.io", "adminUserEnabled": False,
                 "publicNetworkAccess": "Enabled"}, sku={"name": "Premium", "tier": "Premium"})
    mc = "MC_rg-app-prod_aks-prod_westeurope"
    mc_base = f"/subscriptions/{P}/resourceGroups/{mc}/providers"
    kubelet = t.add(P, mc, "Microsoft.ManagedIdentity/userAssignedIdentities", "aks-prod-agentpool",
                    {"principalId": "cccc0000-0000-4000-8000-000000000001",
                     "clientId": "cccc0000-0000-4000-8000-000000000002", "tenantId": TENANT_ID})
    t.add(P, "rg-app-prod", "Microsoft.ContainerService/managedClusters", "aks-prod", {
        "kubernetesVersion": "1.30.4", "dnsPrefix": "aks-prod", "nodeResourceGroup": mc,
        "agentPoolProfiles": [{"name": "system", "count": 3, "vmSize": "Standard_D4s_v5", "mode": "System",
                               "vnetSubnetID": f"{spoke}/subnets/snet-aks", "osType": "Linux"}],
        "addonProfiles": {"omsagent": {"enabled": True, "config": {"logAnalyticsWorkspaceResourceID": law}}},
        "networkProfile": {"networkPlugin": "azure", "serviceCidr": "172.16.0.0/16", "outboundType": "userDefinedRouting"},
        "identityProfile": {"kubeletidentity": {"resourceId": kubelet,
                                                "clientId": "cccc0000-0000-4000-8000-000000000002"}}},
        sku={"name": "Base", "tier": "Standard"}, identity={"type": "SystemAssigned"}, tags={"env": "prod"})
    mc_nsg = t.add(P, mc, f"{net}/networkSecurityGroups", "aks-agentpool-31415926-nsg", {"securityRules": []})
    mc_lb = f"{mc_base}/{net}/loadBalancers/kubernetes-internal"
    t.add(P, mc, f"{net}/loadBalancers", "kubernetes-internal", {
        "frontendIPConfigurations": [{"id": f"{mc_lb}/frontendIPConfigurations/ingress", "name": "ingress",
                                      "properties": {"privateIPAddress": "10.1.16.250",
                                                     "subnet": _ref(f"{spoke}/subnets/snet-aks")}}],
        "backendAddressPools": [{"id": f"{mc_lb}/backendAddressPools/kubernetes", "name": "kubernetes",
                                 "properties": {}}]}, sku={"name": "Standard"})
    t.add(P, mc, "Microsoft.Compute/virtualMachineScaleSets", "aks-system-31415926-vmss", {
        "singlePlacementGroup": False, "orchestrationMode": "Uniform",
        "virtualMachineProfile": {
            "storageProfile": {"osDisk": {"osType": "Linux", "diskSizeGB": 128}},
            "networkProfile": {"networkInterfaceConfigurations": [{"name": "aks-system", "properties": {
                "primary": True, "networkSecurityGroup": _ref(mc_nsg),
                "ipConfigurations": [{"name": "ipconfig1", "properties": {
                    "subnet": _ref(f"{spoke}/subnets/snet-aks"),
                    "loadBalancerBackendAddressPools": [_ref(f"{mc_lb}/backendAddressPools/kubernetes")]}}]}}]}}},
        sku={"name": "Standard_D4s_v5", "tier": "Standard", "capacity": 3},
        identity={"type": "UserAssigned", "userAssignedIdentities": {kubelet: {}}},
        tags={"aks-managed-poolName": "system"}, zones=["1", "2", "3"])

    cae = t.add(P, "rg-app-prod", "Microsoft.App/managedEnvironments", "cae-contoso-prod",
                {"vnetConfiguration": {"infrastructureSubnetId": f"{spoke}/subnets/snet-container-apps",
                                       "internal": True},
                 "staticIp": "10.1.32.10", "zoneRedundant": True,
                 "appLogsConfiguration": {"destination": "log-analytics"}})
    t.add(P, "rg-app-prod", "Microsoft.App/containerApps", "ca-notification-worker",
          {"managedEnvironmentId": cae, "environmentId": cae,
           "configuration": {"activeRevisionsMode": "Single",
                             "registries": [{"server": "acrcontosoprod.azurecr.io", "identity": uami}]},
           "template": {"containers": [{"name": "worker", "image": "acrcontosoprod.azurecr.io/notifier:1.8.2"}],
                        "scale": {"minReplicas": 1, "maxReplicas": 5}}}, identity=identity)

    sb = t.add(P, "rg-app-prod", "Microsoft.ServiceBus/namespaces", "sb-contoso-prod",
               {"serviceBusEndpoint": "https://sb-contoso-prod.servicebus.windows.net:443/", "zoneRedundant": True},
               sku={"name": "Premium", "tier": "Premium", "capacity": 1})
    for queue in ("orders", "invoices", "dead-letter-review"):
        t.child(sb, "queues", "Microsoft.ServiceBus/namespaces/queues", queue,
                {"status": "Active", "maxSizeInMegabytes": 1024, "requiresSession": False})
    t.child(sb, "topics", "Microsoft.ServiceBus/namespaces/topics", "order-events",
            {"status": "Active", "maxSizeInMegabytes": 1024, "subscriptionCount": 2})

    def private_endpoint(name, target_id, group_id, ip, fqdn):
        pe_id = f"{app_net}/privateEndpoints/{name}"
        nic_id = f"{app_net}/networkInterfaces/{name}.nic.1a2b3c4d"
        t.add(P, "rg-app-prod", f"{net}/networkInterfaces", f"{name}.nic.1a2b3c4d", {
            "ipConfigurations": [{"id": f"{nic_id}/ipConfigurations/privateEndpointIpConfig", "name": "privateEndpointIpConfig",
                                  "properties": {"privateIPAddress": ip, "privateIPAllocationMethod": "Dynamic",
                                                 "subnet": _ref(f"{spoke}/subnets/snet-private-endpoints")}}],
            "privateEndpoint": _ref(pe_id)})
        t.add(P, "rg-app-prod", f"{net}/privateEndpoints", name, {
            "subnet": _ref(f"{spoke}/subnets/snet-private-endpoints"), "networkInterfaces": [_ref(nic_id)],
            "privateLinkServiceConnections": [{"name": name, "properties": {
                "privateLinkServiceId": target_id, "groupIds": [group_id],
                "privateLinkServiceConnectionState": {"status": "Approved"}}}],
            "customDnsConfigs": [{"fqdn": fqdn, "ipAddresses": [ip]}]})
        return pe_id

    data_base = f"/subscriptions/{P}/resourceGroups/rg-data-prod/providers"
    sql_id = f"{data_base}/Microsoft.Sql/servers/sql-contoso-prod"
    st_id = f"{data_base}/Microsoft.Storage/storageAccounts/stcontosoprod001"
    kv_id = f"/subscriptions/{P}/resourceGroups/rg-app-prod/providers/Microsoft.KeyVault/vaults/kv-contoso-prod"
    pe_sql = private_endpoint("pe-sql-contoso-prod", sql_id, "sqlServer", "10.1.3.4",
                              "sql-contoso-prod.database.windows.net")
    pe_blob = private_endpoint("pe-stcontosoprod001-blob", st_id, "blob", "10.1.3.5",
                               "stcontosoprod001.blob.core.windows.net")
    pe_kv = private_endpoint("pe-kv-contoso-prod", kv_id, "vault", "10.1.3.6", "kv-contoso-prod.vault.azure.net")
    private_endpoint("pe-partner-api", "/subscriptions/33333333-3333-3333-3333-333333333333/resourceGroups/rg-partner"
                     f"/providers/{net}/privateLinkServices/pls-partner-api", "", "10.1.3.7", "api.partner.example")

    def pe_connection(owner_id, pe_id):
        return [{"id": f"{owner_id}/privateEndpointConnections/{pe_id.rsplit('/', 1)[-1]}",
                 "properties": {"privateEndpoint": _ref(pe_id),
                                "privateLinkServiceConnectionState": {"status": "Approved"}}}]

    t.add(P, "rg-app-prod", "Microsoft.KeyVault/vaults", "kv-contoso-prod", {
        "sku": {"family": "A", "name": "standard"}, "tenantId": TENANT_ID, "enableRbacAuthorization": True,
        "enablePurgeProtection": True, "vaultUri": "https://kv-contoso-prod.vault.azure.net/",
        "publicNetworkAccess": "Disabled", "privateEndpointConnections": pe_connection(kv_id, pe_kv)},
        tags={"env": "prod"})

    # ---- data -----------------------------------------------------------
    t.add(P, "rg-data-prod", "Microsoft.Sql/servers", "sql-contoso-prod", {
        "fullyQualifiedDomainName": "sql-contoso-prod.database.windows.net", "version": "12.0",
        "publicNetworkAccess": "Disabled", "minimalTlsVersion": "1.2",
        "privateEndpointConnections": pe_connection(sql_id, pe_sql)}, kind="v12.0",
        identity={"type": "SystemAssigned"}, tags={"env": "prod"})
    pool = t.add(P, "rg-data-prod", "Microsoft.Sql/servers/elasticPools", "sql-contoso-prod/pool-general",
                 {"state": "Ready", "maxSizeBytes": 536870912000, "zoneRedundant": True},
                 sku={"name": "GP_Gen5", "tier": "GeneralPurpose", "capacity": 4})
    for database in ("db-orders", "db-customers", "db-catalog"):
        t.add(P, "rg-data-prod", "Microsoft.Sql/servers/databases", f"sql-contoso-prod/{database}",
              {"status": "Online", "collation": "SQL_Latin1_General_CP1_CI_AS", "elasticPoolId": pool,
               "zoneRedundant": True}, sku={"name": "ElasticPool", "tier": "GeneralPurpose"}, kind="v12.0,user,pool")
    t.add(P, "rg-data-prod", "Microsoft.Storage/storageAccounts", "stcontosoprod001", {
        "primaryEndpoints": {"blob": "https://stcontosoprod001.blob.core.windows.net/"},
        "supportsHttpsTrafficOnly": True, "minimumTlsVersion": "TLS1_2", "allowBlobPublicAccess": False,
        "networkAcls": {"defaultAction": "Deny", "bypass": "AzureServices"},
        "privateEndpointConnections": pe_connection(st_id, pe_blob)},
        sku={"name": "Standard_ZRS", "tier": "Standard"}, kind="StorageV2", tags={"env": "prod"})
    for container in ("invoices", "exports", "backups"):
        t.child(st_id, "blobServices/default/containers", "Microsoft.Storage/storageAccounts/blobServices/containers",
                container, {"publicAccess": "None", "hasImmutabilityPolicy": False})
    t.child(st_id, "fileServices/default/shares", "Microsoft.Storage/storageAccounts/fileServices/shares",
            "finance-share", {"shareQuota": 100, "accessTier": "TransactionOptimized"})
    cosmos = t.add(P, "rg-data-prod", "Microsoft.DocumentDB/databaseAccounts", "cosmos-contoso-prod", {
        "documentEndpoint": "https://cosmos-contoso-prod.documents.azure.com:443/",
        "databaseAccountOfferType": "Standard", "consistencyPolicy": {"defaultConsistencyLevel": "Session"},
        "locations": [{"locationName": "West Europe", "failoverPriority": 0, "isZoneRedundant": True},
                      {"locationName": "North Europe", "failoverPriority": 1}]}, kind="GlobalDocumentDB")
    t.child(cosmos, "sqlDatabases", "Microsoft.DocumentDB/databaseAccounts/sqlDatabases", "catalog",
            {"resource": {"id": "catalog"}})
    t.add(P, "rg-data-prod", "Microsoft.Cache/Redis", "redis-contoso-prod",
          {"hostName": "redis-contoso-prod.redis.cache.windows.net", "redisVersion": "6.0", "sslPort": 6380,
           "sku": {"name": "Premium", "family": "P", "capacity": 1}})
    t.add(P, "rg-data-prod", "Microsoft.DataFactory/factories", "adf-contoso-prod",
          {"publicNetworkAccess": "Enabled"}, identity={"type": "SystemAssigned"})
    vm_item = "VM;iaasvmcontainerv2;rg-app-prod;vm-web-01"
    t.children[f"{rsv}/backupProtectedItems".lower()] = [{
        "id": f"{rsv}/backupFabrics/Azure/protectionContainers/IaasVMContainer;iaasvmcontainerv2;rg-app-prod;vm-web-01"
              f"/protectedItems/{vm_item}",
        "name": vm_item,
        "type": "Microsoft.RecoveryServices/vaults/backupFabrics/protectionContainers/protectedItems",
        "properties": {"friendlyName": "vm-web-01", "protectedItemType": "Microsoft.Compute/virtualMachines",
                       "sourceResourceId": vm_web[0], "virtualMachineId": vm_web[0],
                       "protectionStatus": "Healthy", "policyId": f"{rsv}/backupPolicies/DefaultPolicy"}}]

    # ---- resource types the tool has no specific knowledge of -------------
    t.add(P, "rg-research", "Microsoft.Quantum/workspaces", "qw-research-lab",
          {"usable": "Yes", "storageAccount": st_id}, identity={"type": "SystemAssigned"})
    t.add(P, "rg-research", "Microsoft.Fabric/capacities", "fabcontosolab",
          {"state": "Active", "administration": {"members": ["admin@contoso.example"]}},
          sku={"name": "F2", "tier": "Fabric"})
    t.add(P, "rg-research", "Microsoft.MachineLearningServices/workspaces",
          "mlw-contoso-research-experiments-westeurope-001",
          {"friendlyName": "Research experiments", "storageAccount": st_id, "keyVault": kv_id,
           "applicationInsights": appi, "containerRegistry": acr}, identity={"type": "SystemAssigned"},
          sku={"name": "Basic", "tier": "Basic"}, kind="Default")
    t.graph_hidden_types.add("microsoft.quantum/workspaces")
    t.api_overrides["microsoft.quantum/workspaces"] = ["2019-11-04-preview", "2022-01-10-preview"]

    # ---- dev/test subscription -------------------------------------------
    nsg_dev = t.add(D, "rg-dev", f"{net}/networkSecurityGroups", "nsg-dev-default",
                    {"securityRules": [{"name": "AllowSshFromOffice", "properties": {
                        "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp",
                        "sourceAddressPrefix": "203.0.113.0/24", "destinationPortRange": "22"}}],
                     "subnets": [_ref(f"{dev}/subnets/snet-default")]})
    t.add(D, "rg-dev", f"{net}/virtualNetworks", "vnet-dev", {
        "addressSpace": {"addressPrefixes": ["10.50.0.0/16"]},
        "subnets": [_subnet(dev, "snet-default", "10.50.0.0/24", nsg=nsg_dev),
                    _subnet(dev, "snet-spare", "10.50.1.0/24")],
        "virtualNetworkPeerings": [_peering(dev, "dev-to-hub", hub, use_remote_gateways=True)]},
        tags={"env": "dev"})
    vm_dev = virtual_machine(D, "rg-dev", "vm-dev-01", f"{dev}/subnets/snet-default", "10.50.0.4",
                             size="Standard_B2ms", os_type="Linux", public="20.50.99.7", tags={"env": "dev"})
    t.add(D, "rg-dev", "Microsoft.DevTestLab/schedules", "shutdown-computevm-vm-dev-01",
          {"status": "Enabled", "taskType": "ComputeVmShutdownTask", "dailyRecurrence": {"time": "1900"},
           "timeZoneId": "Romance Standard Time", "targetResourceId": vm_dev})
    dev_plan = t.add(D, "rg-dev", "Microsoft.Web/serverFarms", "asp-dev", {"numberOfSites": 1},
                     sku={"name": "B1", "tier": "Basic", "capacity": 1}, kind="linux")
    t.add(D, "rg-dev", "Microsoft.Web/sites", "app-contoso-portal-dev",
          {"serverFarmId": dev_plan, "httpsOnly": True, "state": "Running",
           "defaultHostName": "app-contoso-portal-dev.azurewebsites.net"}, kind="app,linux")
    t.add(D, "rg-dev", "Microsoft.Web/staticSites", "stapp-contoso-docs",
          {"defaultHostname": "calm-sea-0a1b2c3d4.azurestaticapps.net",
           "repositoryUrl": "https://github.com/contoso/docs"}, sku={"name": "Free", "tier": "Free"})
    dev_st = t.add(D, "rg-dev", "Microsoft.Storage/storageAccounts", "stcontosodev",
                   {"primaryEndpoints": {"blob": "https://stcontosodev.blob.core.windows.net/"},
                    "supportsHttpsTrafficOnly": True, "allowBlobPublicAccess": True},
                   sku={"name": "Standard_LRS", "tier": "Standard"}, kind="StorageV2")
    t.child(dev_st, "blobServices/default/containers", "Microsoft.Storage/storageAccounts/blobServices/containers",
            "scratch", {"publicAccess": "Blob"})
    connection = t.add(D, "rg-dev", "Microsoft.Web/connections", "office365",
                       {"displayName": "ops@contoso.example", "statuses": [{"status": "Connected"}],
                        "api": {"id": f"/subscriptions/{D}/providers/Microsoft.Web/locations/westeurope"
                                      "/managedApis/office365"}})
    t.add(D, "rg-dev", "Microsoft.Logic/workflows", "logic-nightly-report",
          {"state": "Enabled", "definition": {"triggers": {"Recurrence": {"type": "Recurrence"}}},
           "parameters": {"$connections": {"value": {"office365": {"connectionId": connection}}}}})
    t.add(D, "NetworkWatcherRG", f"{net}/networkWatchers", "NetworkWatcher_westeurope", {})

    # ---- Azure Advisor ----------------------------------------------------
    t.recommend(P, vm_web[1], "Cost", "High", "Right-size or shutdown underutilized virtual machines",
                "Resize vm-web-02 to Standard_D2s_v5")
    t.recommend(P, vm_dc, "HighAvailability", "Medium", "Enable backups on your virtual machines",
                "Protect vm-dc-01 with Azure Backup")
    t.recommend(P, f"{sql_id}/databases/db-orders", "Security", "High",
                "SQL databases should have vulnerability findings resolved", "Review the vulnerability assessment")
    t.recommend(P, f"/subscriptions/{P}", "Cost", "Medium", "Consider a savings plan for compute",
                "Review the savings plan recommendation")
    t.recommend(D, dev_st, "Security", "High", "Storage account public access should be disallowed",
                "Disable anonymous blob access on stcontosodev")
    return t


def _basic(resource):
    """What the ARM resource *listing* returns: everything except properties."""
    return {key: value for key, value in resource.items() if key != "properties"}


class FakeAzure:
    """HTTP server speaking just enough ARM for the collector."""

    def __init__(self, tenant=None, list_page_size=25, graph_page_cap=40):
        self.tenant = tenant or build_tenant()
        self.list_page_size = list_page_size
        self.graph_page_cap = graph_page_cap
        self.requests = []          # (method, path) of every call received
        self.fail_graph = False     # make Resource Graph answer 403
        self._throttle_once = True  # first Resource Graph call is answered with 429
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.endpoint = f"http://127.0.0.1:{self._server.server_address[1]}"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *_):
        self._server.shutdown()
        self._server.server_close()

    # -- request handling --------------------------------------------------
    def _handler(self):
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):  # keep test output quiet
                pass

            def _reply(self, status, payload, headers=None):
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                for key, value in (headers or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(body)

            def _dispatch(self, method):
                parsed = urlparse(self.path)
                path, query = unquote(parsed.path), parse_qs(parsed.query)
                fake.requests.append((method, path))
                if self.headers.get("Authorization") != f"Bearer {TOKEN}":
                    return self._reply(401, {"error": {"code": "AuthenticationFailed", "message": "bad token"}})
                body = {}
                if method == "POST":
                    body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
                status, payload, headers = fake.route(method, path, query, body)
                return self._reply(status, payload, headers)

            def do_GET(self):  # noqa: N802
                self._dispatch("GET")

            def do_POST(self):  # noqa: N802
                self._dispatch("POST")

        return Handler

    def _page(self, items, path, query):
        """ARM style paging with nextLink."""
        offset = int((query.get("offset") or ["0"])[0])
        page = items[offset:offset + self.list_page_size]
        payload = {"value": page}
        if offset + self.list_page_size < len(items):
            api = (query.get("api-version") or [""])[0]
            payload["nextLink"] = f"{self.endpoint}{path}?api-version={api}&offset={offset + self.list_page_size}"
        return 200, payload, None

    def route(self, method, path, query, body):
        tenant, lower = self.tenant, path.lower().rstrip("/")
        api_version = (query.get("api-version") or [""])[0]
        if not api_version:
            return _error(400, "MissingApiVersionParameter", "The api-version query parameter is required.")

        if method == "POST" and lower == "/providers/microsoft.resourcegraph/resources":
            return self._graph(body)
        if lower == "/subscriptions":
            return self._page(tenant.subscriptions, path, query)

        match = re.match(r"^/subscriptions/([^/]+)(/.*)?$", path)
        if not match or match.group(1) not in tenant.groups:
            return _error(404, "SubscriptionNotFound", f"The subscription in '{path}' could not be found.")
        subscription_id, rest = match.group(1), (match.group(2) or "").lower()
        in_subscription = [r for r in tenant.resources if r["id"].split("/")[2] == subscription_id]

        if rest == "/providers":
            return self._page(self._providers(), path, query)
        if rest == "/resourcegroups":
            return self._page(tenant.groups[subscription_id], path, query)
        if rest == "/resources":
            return self._page([_basic(r) for r in in_subscription], path, query)
        group_listing = re.match(r"^/resourcegroups/([^/]+)/resources$", rest)
        if group_listing:
            wanted = group_listing.group(1)
            if wanted not in {g["name"].lower() for g in tenant.groups[subscription_id]}:
                return _error(404, "ResourceGroupNotFound", f"Resource group '{wanted}' could not be found.")
            return self._page([_basic(r) for r in in_subscription if r["id"].split("/")[4].lower() == wanted],
                              path, query)
        if rest == "/providers/microsoft.advisor/recommendations":
            return self._page(tenant.recommendations[subscription_id], path, query)

        if lower in tenant.children:
            return self._page(tenant.children[lower], path, query)
        for resource in in_subscription:
            if resource["id"].lower() == lower:
                return self._get(resource, api_version)
        for resource in in_subscription:
            if lower.startswith(resource["id"].lower() + "/"):
                return self._page([], path, query)  # a child collection without content
        return _error(404, "ResourceNotFound", f"The resource '{path}' was not found.")

    def _providers(self):
        """Provider metadata for every type that exists in the tenant."""
        types = {r["type"] for r in self.tenant.resources}
        types |= {child["type"] for children in self.tenant.children.values() for child in children}
        types.add("Microsoft.RecoveryServices/vaults/backupProtectedItems")
        providers = {}
        for resource_type in sorted(types):
            namespace, rest = resource_type.split("/", 1)
            entry = {"resourceType": rest, "apiVersions": ["2025-01-01-preview", "2024-01-01", "2022-01-01"]}
            if resource_type.lower() in self.tenant.api_overrides:
                entry["apiVersions"] = ["2099-01-01"]  # metadata that does not match reality
            else:
                entry["defaultApiVersion"] = "2022-01-01"
            providers.setdefault(namespace, []).append(entry)
        return [{"id": f"/providers/{namespace}", "namespace": namespace, "registrationState": "Registered",
                 "resourceTypes": entries} for namespace, entries in providers.items()]

    def _get(self, resource, api_version):
        accepted = self.tenant.api_overrides.get(resource["type"].lower())
        if accepted and api_version not in accepted:
            type_name = resource["type"].split("/", 1)[1]
            return _error(400, "NoRegisteredProviderFound",
                          f"No registered resource provider found for location 'westeurope' and API version "
                          f"'{api_version}' for type '{type_name}'. The supported api-versions are "
                          f"'{', '.join(accepted)}'. The supported locations are 'westeurope'.")
        return 200, resource, None

    def _graph(self, body):
        if self.fail_graph:
            return _error(403, "AuthorizationFailed", "The client does not have authorization to perform action "
                                                      "'Microsoft.ResourceGraph/resources/read'.")
        if self._throttle_once:
            self._throttle_once = False
            return 429, {"error": {"code": "RateLimiting", "message": "Please retry later."}}, {"Retry-After": "0"}
        subscriptions = set(body.get("subscriptions") or [])
        query, options = body.get("query") or "", body.get("options") or {}
        if not query.strip().lower().startswith("resources"):
            return _error(400, "BadRequest", "Only the resources table is available in this fake.")
        rows = []
        group_filter = re.search(r"resourceGroup\s*=~\s*'((?:[^'\\]|\\.)*)'", query)
        for resource in self.tenant.resources:
            parts = resource["id"].split("/")
            if parts[2] not in subscriptions or resource["type"].lower() in self.tenant.graph_hidden_types:
                continue
            if group_filter and parts[4].lower() != group_filter.group(1).lower():
                continue
            # Resource Graph lower-cases type and resourceGroup and adds a few columns of its own.
            rows.append({**resource, "type": resource["type"].lower(), "resourceGroup": parts[4].lower(),
                         "subscriptionId": parts[2], "tenantId": TENANT_ID,
                         "kind": resource.get("kind", ""), "managedBy": resource.get("managedBy", ""),
                         "sku": resource.get("sku"), "plan": None})
        rows.sort(key=lambda row: row["id"].lower())
        offset = int(options.get("$skipToken") or 0)
        size = min(int(options.get("$top") or 100), self.graph_page_cap)
        payload = {"totalRecords": len(rows), "count": len(rows[offset:offset + size]),
                   "data": rows[offset:offset + size], "resultTruncated": "false"}
        if offset + size < len(rows):
            payload["$skipToken"] = str(offset + size)
        return 200, payload, None


def _error(status, code, message):
    return status, {"error": {"code": code, "message": message}}, None


def collect_sample(**option_overrides):
    """Run the real collector against the fake tenant and return the inventory."""
    from azure_func.arm import ArmClient
    from azure_func.collector import Collector, CollectorOptions

    with FakeAzure() as fake:
        arm = ArmClient(FakeCredential(), fake.endpoint)
        try:
            return Collector(arm, CollectorOptions(**option_overrides), progress=None).collect()
        finally:
            arm.close()


def write_example(folder):
    """Regenerate the files in ``example output/`` from the fake tenant."""
    import os

    import main
    from functions import parse_arguments

    os.makedirs(folder, exist_ok=True)
    data = collect_sample()
    main.write_json(data, os.path.join(folder, "output.json"))
    args = parse_arguments(["--output_xlsx", "--output_drawio"])
    failed = main.write_outputs(data, args, folder)
    if failed:
        raise SystemExit(f"Could not write: {', '.join(failed)}")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")
    write_example(sys.argv[1] if len(sys.argv) > 1 else "example output")
