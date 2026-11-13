"""The collector against the fake ARM API: coverage, fallbacks and filters."""
import pytest

from azure_func.arm import ArmError
from azure_func.collector import Collector, CollectorOptions, normalize_resource
from tests.fake_azure import SUB_DEV, SUB_PROD, build_tenant


def entries(data):
    return [entry for groups in data["Objects"].values() for group in groups.values() for entry in group]


def by_name(data, name):
    return next(entry for entry in entries(data) if entry["Details"]["name"] == name)


def collect(arm, **options):
    return Collector(arm, CollectorOptions(**options), progress=None).collect()


def test_every_resource_of_the_tenant_is_collected(sample):
    tenant = build_tenant()
    collected = {entry["Details"]["id"].lower() for entry in entries(sample)}
    expected = {resource["id"].lower() for resource in tenant.resources}
    assert expected <= collected
    for children in tenant.children.values():
        assert {child["id"].lower() for child in children} <= collected


def test_document_structure(sample):
    assert set(sample) == {"Properties", "Subscriptions", "ResourceGroups", "Objects"}
    assert sample["Properties"]["Engine"] == "Resource Graph"
    assert sample["Subscriptions"][SUB_PROD]["displayName"] == "Contoso Production"
    assert "rg-sandbox-empty" in sample["Objects"][SUB_PROD], "empty resource groups are kept"
    assert sample["Objects"][SUB_PROD]["rg-sandbox-empty"] == []
    assert sample["ResourceGroups"][SUB_PROD]["rg-app-prod"]["tags"]["owner"] == "app-team"
    for entry in entries(sample):
        assert set(entry) == {"ResourceType", "Details", "Recommendations"}
        assert isinstance(entry["Details"], dict) and entry["Details"]["id"]


def test_types_use_arm_casing_and_resource_groups_their_real_name(sample):
    vm = by_name(sample, "vm-web-01")
    assert vm["ResourceType"] == "Microsoft.Compute/virtualMachines"  # Resource Graph returns lower case
    assert vm["Details"]["properties"]["hardwareProfile"]["vmSize"] == "Standard_D4s_v5"
    assert "MC_rg-app-prod_aks-prod_westeurope" in sample["Objects"][SUB_PROD]


def test_unknown_types_get_full_properties(sample):
    """A type the tool knows nothing about, missing from Resource Graph, whose
    advertised API version is wrong: still collected with all its properties."""
    workspace = by_name(sample, "qw-research-lab")
    assert workspace["ResourceType"] == "Microsoft.Quantum/workspaces"
    assert workspace["Details"]["properties"]["usable"] == "Yes"
    assert by_name(sample, "fabcontosolab")["Details"]["sku"]["name"] == "F2"


def test_child_resources(sample):
    types = {entry["ResourceType"] for entry in entries(sample)}
    assert {"Microsoft.ServiceBus/namespaces/queues", "Microsoft.ServiceBus/namespaces/topics",
            "Microsoft.Storage/storageAccounts/blobServices/containers",
            "Microsoft.Storage/storageAccounts/fileServices/shares",
            "Microsoft.Web/sites/functions", "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/virtualNetworks/virtualNetworkPeerings",
            "Microsoft.RecoveryServices/vaults/backupFabrics/protectionContainers/protectedItems"} <= types
    subnets = [e for e in entries(sample) if e["ResourceType"] == "Microsoft.Network/virtualNetworks/subnets"]
    assert len(subnets) == 12


def test_skip_children(arm):
    data = collect(arm, include_children=False)
    types = {entry["ResourceType"] for entry in entries(data)}
    assert "Microsoft.ServiceBus/namespaces/queues" not in types
    assert "Microsoft.Network/virtualNetworks/subnets" not in types
    assert "Microsoft.Sql/servers/databases" in types, "tracked child resources are regular resources"


def test_advisor_recommendations(sample):
    assert len(by_name(sample, "vm-web-02")["Recommendations"]) == 1
    recommendation = by_name(sample, "stcontosodev")["Recommendations"][0]
    assert recommendation["properties"]["impact"] == "High"
    # subscription level recommendations are kept with the subscription
    assert len(sample["Subscriptions"][SUB_PROD]["Recommendations"]) == 1
    assert "Recommendations" not in sample["Subscriptions"][SUB_DEV]


def test_skip_advisor(arm, fake_azure):
    data = collect(arm, include_advisor=False)
    assert all(entry["Recommendations"] == [] for entry in entries(data))
    assert not any("advisor" in path.lower() for _, path in fake_azure.requests)


def test_throttling_is_retried(arm, fake_azure):
    collect(arm)
    graph_calls = [path for method, path in fake_azure.requests if method == "POST"]
    assert len(graph_calls) >= 3, "429, then at least one page per subscription"


def test_falls_back_to_arm_when_resource_graph_is_unavailable(arm, fake_azure, sample):
    fake_azure.fail_graph = True
    data = collect(arm)
    assert data["Properties"]["Engine"] == "ARM"
    assert {e["Details"]["id"].lower() for e in entries(data)} == {e["Details"]["id"].lower() for e in entries(sample)}
    vm = by_name(data, "vm-web-01")
    assert vm["Details"]["properties"]["hardwareProfile"]["vmSize"] == "Standard_D4s_v5"


def test_graph_only_engine_reports_failure(arm, fake_azure):
    fake_azure.fail_graph = True
    data = collect(arm, engine="graph")
    assert "AuthorizationFailed" in data["Subscriptions"][SUB_PROD]["Error"]
    assert entries(data) == []


def test_arm_engine_matches_resource_graph(arm, sample):
    data = collect(arm, engine="arm")
    assert {e["Details"]["id"].lower() for e in entries(data)} == {e["Details"]["id"].lower() for e in entries(sample)}


@pytest.mark.parametrize("engine", ["auto", "arm"])
def test_resource_group_filter(arm, engine):
    data = collect(arm, engine=engine, resource_group="RG-DATA-PROD")  # case-insensitive
    assert list(data["Objects"][SUB_PROD]) == ["rg-data-prod"]
    assert data["Objects"][SUB_DEV] == {}
    names = {entry["Details"]["name"] for entry in entries(data)}
    assert "sql-contoso-prod" in names and "vm-web-01" not in names
    assert "invoices" in names, "children of matching resources are included"


def test_resource_group_tag_filter(arm):
    data = collect(arm, rgtag_key="owner", rgtag_value="data-team")
    assert list(data["Objects"][SUB_PROD]) == ["rg-data-prod"]
    assert len(entries(data)) > 5


def test_resource_tag_filter(arm):
    data = collect(arm, rtag_key="role", rtag_value="web")
    names = {entry["Details"]["name"] for entry in entries(data)}
    assert names == {"vm-web-01", "vm-web-02"}


def test_selected_subscription_only(arm):
    data = Collector(arm, CollectorOptions(), progress=None).collect([SUB_DEV])
    assert list(data["Objects"]) == [SUB_DEV]
    assert data["Subscriptions"][SUB_DEV]["displayName"] == "Contoso Dev/Test"


def test_unknown_subscription_is_reported_not_fatal(arm):
    data = Collector(arm, CollectorOptions(), progress=None).collect(["00000000-0000-0000-0000-000000000000", SUB_DEV])
    assert "Error" in data["Subscriptions"]["00000000-0000-0000-0000-000000000000"]
    assert len(data["Objects"][SUB_DEV]["rg-dev"]) > 5


def test_arm_client_errors_and_paging(arm, fake_azure):
    with pytest.raises(ArmError) as error:
        arm.get("/subscriptions/nope/resourcegroups", "2021-04-01")
    assert error.value.status_code == 404 and error.value.code == "SubscriptionNotFound"
    listed = list(arm.list(f"/subscriptions/{SUB_PROD}/resources", "2021-04-01"))
    assert len(listed) > fake_azure.list_page_size, "nextLink paging is followed"
    assert len({item["id"] for item in listed}) == len(listed)


def test_names_with_spaces_are_requested_correctly(arm):
    resource_id = (f"/subscriptions/{SUB_PROD}/resourceGroups/rg-app-prod/providers/Microsoft.Insights/actionGroups/"
                   "Application Insights Smart Detection")
    assert arm.get(resource_id, "2022-01-01")["name"] == "Application Insights Smart Detection"


def test_normalize_drops_empty_values():
    raw = {"id": "/x", "name": "n", "type": "t", "kind": "", "managedBy": "", "sku": None, "tags": {},
           "tenantId": "t", "resourceGroup": "rg", "properties": {"a": 1}}
    assert normalize_resource(raw) == {"id": "/x", "name": "n", "type": "t", "properties": {"a": 1}}
