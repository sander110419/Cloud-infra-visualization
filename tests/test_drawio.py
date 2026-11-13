"""Relationship discovery, icons and the draw.io document."""
import base64
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter

import pytest

from azure_func import icons
from azure_func.drawio_library import LIBRARY_ICONS
from azure_func.inventory import Inventory, parent_resource_id, type_of_id
from json2drawio import HIDDEN_ON_RESOURCE_PAGES, Model, Network, build_drawio, generate_drawio

SUB = "/subscriptions/s/resourceGroups/rg/providers"


def node(inventory, name, type_contains=""):
    return next(n for n in inventory.nodes.values() if n.name == name and type_contains.lower() in n.type_lower)


# ---- inventory --------------------------------------------------------------
def test_parent_resource_id():
    assert parent_resource_id(f"{SUB}/Microsoft.Sql/servers/a/databases/b") == f"{SUB}/Microsoft.Sql/servers/a"
    assert parent_resource_id(f"{SUB}/Microsoft.Sql/servers/a") is None
    lock = f"{SUB}/Microsoft.Sql/servers/a/providers/Microsoft.Authorization/locks/l"
    assert parent_resource_id(lock) == f"{SUB}/Microsoft.Sql/servers/a"
    assert type_of_id(f"{SUB}/Microsoft.Network/virtualNetworks/v/subnets/s") == "Microsoft.Network/virtualNetworks/subnets"


def test_hierarchy_and_references(sample):
    inventory = Inventory(sample)
    database = node(inventory, "sql-contoso-prod/db-orders")
    assert database.parent.name == "sql-contoso-prod"
    container = node(inventory, "invoices", "blobServices")  # .../blobServices/default/containers/invoices
    assert container.parent.name == "stcontosoprod001"

    vm = node(inventory, "vm-web-01")
    assert {inventory.nodes[key].name for key in vm.refs} == {
        "vm-web-01-nic", "vm-web-01-osdisk", "vm-web-01-datadisk-0", "avail-web"}
    # references found in keys (user assigned identities) and in tags
    app = node(inventory, "app-contoso-portal")
    referenced = {inventory.nodes[key].name for key in app.refs}
    assert {"id-app-prod", "asp-contoso-prod", "appi-contoso-prod", "snet-integration"} <= referenced
    # a resource of an unknown type is linked like any other
    assert {inventory.nodes[key].name for key in node(inventory, "qw-research-lab").refs} == {"stcontosoprod001"}
    # nothing points at itself or at its own parent
    for item in inventory.nodes.values():
        assert item.key not in item.refs
        assert all(ancestor.key not in item.refs for ancestor in item.ancestors())


def test_reads_inventories_written_by_older_versions():
    old = {"Objects": {"sub": {"rg": [
        {"ResourceType": "Microsoft.Web/sites",
         "Details": [{"id": f"{SUB}/Microsoft.Web/sites/app/functions/f1", "name": "app/f1"}]},
        {"ResourceType": "Microsoft.Sql/servers", "Details": {"Error": "boom"}},
        {"ResourceType": "Microsoft.Compute/disks",
         "Details": {"id": f"{SUB}/Microsoft.Compute/disks/d", "name": "d", "type": "Microsoft.Compute/disks"}},
    ]}}}
    assert len(Inventory(old).nodes) == 2
    document = build_drawio(old).getroot()
    assert len(document.findall("diagram")) == 1


# ---- icons ------------------------------------------------------------------
def test_every_mapped_icon_exists():
    stems = {icon for icon, _ in icons.RESOURCE_TYPES.values()}
    stems |= {icon for icon, _ in icons.PROVIDERS.values() if icon}
    stems |= {icon for icon, _ in icons._COGNITIVE_KINDS.values()}
    stems |= {icons.DEFAULT_ICON, "Subscriptions", "Resource-Groups", "Subnet", "Connections"}
    missing = [stem for stem in stems if not os.path.exists(os.path.join(icons.icon_dir(), f"{stem}.svg"))]
    assert missing == []
    assert all(key == key.lower() for key in icons.RESOURCE_TYPES)
    assert {category for _, category in icons.PROVIDERS.values()} <= set(icons.CATEGORY_ORDER)


def test_library_icons_have_a_local_fallback():
    for stem in LIBRARY_ICONS:
        assert os.path.exists(os.path.join(icons.icon_dir(), f"{stem}.svg")), stem


@pytest.mark.parametrize("resource_type, kind, sku, icon, name", [
    ("Microsoft.Compute/virtualMachines", "", "", "Virtual-Machine", "Virtual machine"),
    ("microsoft.web/sites", "functionapp,linux", "", "Function-Apps", "Function app"),
    ("Microsoft.Web/sites", "functionapp,workflowapp", "", "Logic-Apps", "Logic app (Standard)"),
    ("Microsoft.Web/sites", "app", "", "App-Services", "App Service"),
    ("Microsoft.CognitiveServices/accounts", "OpenAI", "", "Azure-OpenAI", "Azure OpenAI"),
    ("Microsoft.Cdn/profiles", "", "Standard_AzureFrontDoor", "Front-Door-and-CDN-Profiles", "Front Door profile"),
    ("Microsoft.Cdn/profiles", "", "Standard_Microsoft", "CDN-Profiles", "CDN profile"),
    # unknown type of a known provider: provider icon, readable name
    ("Microsoft.ApiManagement/service/products", "", "", "API-Management-Services", "Product"),
    # completely unknown: generic icon
    ("Contoso.Widgets/widgetFactories", "", "", icons.DEFAULT_ICON, "Widget factory"),
    ("Microsoft.Network/publicIPAddresses", "", "", "Public-IP-Addresses", "Public IP address"),
])
def test_describe(resource_type, kind, sku, icon, name):
    assert icons.describe(resource_type, kind, sku) == (icon, name)


# ---- draw.io ----------------------------------------------------------------
@pytest.fixture(scope="module")
def document(_sample):
    return build_drawio(_sample).getroot()


def cells(diagram):
    """[(attributes of the wrapper or cell, mxCell element)] for every cell of a page."""
    result = []
    for element in diagram.find("mxGraphModel/root"):
        if element.tag == "object":
            result.append((element.attrib, element.find("mxCell")))
        else:
            result.append((element.attrib, element))
    return result


def test_pages(document):
    names = [diagram.get("name") for diagram in document.findall("diagram")]
    assert names == ["Contoso Dev/Test", "Contoso Production", "Network topology"]
    assert document.get("pages") == "3"


def test_document_is_consistent(document):
    """Unique ids, and every parent / edge terminal points at an existing cell."""
    for diagram in document.findall("diagram"):
        page_cells = cells(diagram)
        ids = [attributes["id"] for attributes, _ in page_cells]
        assert len(ids) == len(set(ids))
        known = set(ids)
        for _, cell in page_cells:
            for reference in ("parent", "source", "target"):
                if cell.get(reference) is not None:
                    assert cell.get(reference) in known
            if cell.get("vertex") == "1":
                geometry = cell.find("mxGeometry")
                assert float(geometry.get("width")) > 0 and float(geometry.get("height")) > 0
            if cell.get("edge") == "1" and cell.get("source") is not None:
                assert cell.get("source") != cell.get("target")
    all_ids = [attributes["id"] for diagram in document.findall("diagram") for attributes, _ in cells(diagram)]
    assert len(all_ids) == len(set(all_ids)), "ids are unique across pages too"


def test_every_resource_is_drawn_once_on_its_subscription_page(document, _sample):
    inventory = Inventory(_sample)
    expected = Counter(n.id for n in inventory.nodes.values() if n.type_lower not in HIDDEN_ON_RESOURCE_PAGES)
    drawn = Counter()
    for diagram in document.findall("diagram")[:2]:
        for attributes, cell in cells(diagram):
            if cell.get("vertex") == "1" and attributes.get("resourceId", "").count("/providers/"):
                drawn[attributes["resourceId"]] += 1
    assert drawn == expected


def test_shapes_carry_data_and_portal_link(document):
    production = document.findall("diagram")[1]
    vm = next(attributes for attributes, _ in cells(production) if attributes.get("name") == "vm-web-01")
    assert vm["type"] == "Microsoft.Compute/virtualMachines"
    assert vm["resourceGroup"] == "rg-app-prod" and vm["subscription"] == "Contoso Production"
    assert vm["tag_role"] == "web" and vm["tag_env"] == "prod"
    assert "zones" not in vm, "empty values are left out"
    assert vm["link"].startswith("https://portal.azure.com/#@99999999-9999-9999-9999-999999999999/resource/subscriptions/")
    assert "<b>vm-web-01</b>" in vm["label"].replace("\u200b", "") and "Virtual machine" in vm["label"]


def test_icons_are_embedded_svg(document):
    production = document.findall("diagram")[1]
    styles = [cell.get("style", "") for _, cell in cells(production) if cell.get("vertex") == "1"]
    images = [re.search(r"image=([^;]+);", style).group(1) for style in styles if "image=" in style]
    assert len(images) > 100
    for image in images:
        assert image.startswith("data:image/svg+xml,")
        assert b"<svg" in base64.b64decode(image.split(",", 1)[1])


def test_library_icons_make_the_file_much_smaller(_sample, tmp_path):
    embedded = generate_drawio(_sample, str(tmp_path / "embedded.drawio"))
    library = generate_drawio(_sample, str(tmp_path / "library.drawio"), icons="library")
    assert os.path.getsize(library) < os.path.getsize(embedded) * 0.5
    text = open(library, encoding="utf-8").read()
    assert "image=img/lib/azure2/compute/Virtual_Machine.svg" in text
    ET.parse(library)


def test_library_icons_keep_their_proportions():
    image, width, height = icons.drawio_image("Virtual-Networks", "library", 48)
    assert image == "img/lib/azure2/networking/Virtual_Networks.svg"
    assert width == 48 and height < 48, "draw.io's icon is wider than it is tall"
    assert icons.drawio_image("Virtual-Networks", "embedded", 48)[1:] == (48, 48)
    # no draw.io counterpart: embedded even in library mode
    assert icons.drawio_image("Auto-Scale", "library", 32)[0].startswith("data:image/svg+xml,")


def test_related_resources_are_boxed_together(_sample):
    model = Model(_sample)
    vm = node(model.inventory, "vm-web-01")
    names = {member.name for member in model.descendants(vm)}
    assert names == {"vm-web-01-nic", "vm-web-01-osdisk", "vm-web-01-datadisk-0", "vm-web-01/AzureMonitorAgent"}
    plan = node(model.inventory, "asp-contoso-prod")
    assert {"app-contoso-portal", "func-contoso-orders", "ProcessOrder"} <= {m.name for m in model.descendants(plan)}
    endpoint = node(model.inventory, "pe-sql-contoso-prod")
    assert [m.name for m in model.descendants(endpoint)] == ["pe-sql-contoso-prod.nic.1a2b3c4d"]
    # a public IP follows its NIC into the VM box
    dev_vm = node(model.inventory, "vm-dev-01")
    assert "vm-dev-01-pip" in {m.name for m in model.descendants(dev_vm)}


def test_links_between_resources(document):
    production = document.findall("diagram")[1]
    page_cells = cells(production)
    layers = {attributes.get("value") for attributes, cell in page_cells if cell.get("parent", "").endswith("-0")}
    assert {"Resources", "Links - network", "Links - monitoring", "Links - identity & security"} <= layers
    links = {(attributes.get("from"), attributes.get("to")) for attributes, cell in page_cells if cell.get("edge") == "1"}
    assert ("pe-sql-contoso-prod", "sql-contoso-prod") in links
    assert ("qw-research-lab", "stcontosoprod001") in links, "unknown types are linked too"
    # drawn inside each other, so no line needed
    assert not any({"vm-web-01", "vm-web-01-nic"} == set(link) for link in links)
    # where things are deployed is left to the network page
    assert not any("vnet-app-prod" in link and "aks-prod" in link for link in links)


def test_network_placement(_sample):
    model = Model(_sample)
    network = Network(model)
    assert len(network.vnets) == 3 and len(network.subnets) == 12

    def placed_in(subnet_name):
        subnet_id = next(key for key in network.subnets if key.endswith(f"/subnets/{subnet_name}"))
        return {owner.name for owner in network.in_subnet[subnet_id]}

    assert placed_in("snet-web") == {"vm-web-01", "vm-web-02", "lbi-web"}            # NICs shown as their VM
    assert placed_in("snet-private-endpoints") == {"pe-sql-contoso-prod", "pe-kv-contoso-prod",
                                                   "pe-stcontosoprod001-blob", "pe-partner-api"}
    assert placed_in("snet-integration") == {"app-contoso-portal", "func-contoso-orders"}
    assert placed_in("snet-aks") == {"aks-prod", "aks-system-31415926-vmss", "kubernetes-internal"}
    assert placed_in("gatewaysubnet") == {"vgw-hub"}
    assert placed_in("snet-spare") == set()
    hub = node(model.inventory, "vnet-hub")
    assert len(network.dns_zones[hub.key]) == 3
    private, public = network.addresses(node(model.inventory, "vm-dev-01"))
    assert private == ["10.50.0.4"] and public == ["20.50.99.7"]


def test_network_page(document):
    page_cells = cells(document.findall("diagram")[2])
    subnets = [a for a, _ in page_cells if a.get("type") == "Microsoft.Network/virtualNetworks/subnets"]
    assert len(subnets) == 12
    web = next(a for a in subnets if a["name"] == "snet-web")
    assert web["addressPrefix"] == "10.1.1.0/24" and web["nsg"] == "nsg-web" and web["routes"] == "rt-spokes-via-firewall"
    edges = [a for a, cell in page_cells if cell.get("edge") == "1" and cell.get("source")]
    peerings = [a for a in edges if a.get("tags") == "link peering"]
    assert len(peerings) == 3, "hub-app, hub-dev (both sides collapse into one link) and hub-partner"
    assert any(a.get("tags") == "link gateway" and a.get("connection") == "cn-hub-to-brussels" for a in edges)
    private_links = {(a["from"], a["to"]) for a in edges if a.get("tags") == "link privatelink"}
    assert ("pe-sql-contoso-prod", "sql-contoso-prod") in private_links
    assert ("pe-partner-api", "pls-partner-api") in private_links
    # things outside the inventory are drawn as placeholders
    remarks = [a for a, _ in page_cells if a.get("remark") == "outside this inventory"]
    assert {a["name"] for a in remarks} == {"vnet-partner-shared", "pls-partner-api"}


def test_no_network_page_without_virtual_networks(_sample):
    data = {"Objects": {"sub": {"rg": [entry for entry in _sample["Objects"][next(iter(_sample["Objects"]))]["rg-monitoring"]]}}}
    names = [diagram.get("name") for diagram in build_drawio(data).getroot().findall("diagram")]
    assert names == ["sub"]


def test_empty_inventory_still_gives_a_valid_file(tmp_path):
    path = generate_drawio({"Objects": {}}, str(tmp_path / "empty.drawio"))
    assert len(ET.parse(path).getroot().findall("diagram")) == 1


def test_awkward_names_do_not_break_the_xml(tmp_path):
    name = 'we"ird <name> & co \u00e9\u00e8 ' + "x" * 80
    data = {"Objects": {"sub": {"rg <1> & \"2\"": [{
        "ResourceType": "Microsoft.Storage/storageAccounts",
        "Details": {"id": f"{SUB}/Microsoft.Storage/storageAccounts/{name}", "name": name,
                    "type": "Microsoft.Storage/storageAccounts", "tags": {"my tag/1": "<v>", "2nd": "x"}}}]}}}
    root = ET.parse(generate_drawio(data, str(tmp_path / "odd.drawio"))).getroot()
    shape = next(element for element in root.iter("object") if element.get("resourceId"))
    assert shape.get("name") == name and shape.get("tag_my_tag_1") == "<v>" and shape.get("tag_2nd") == "x"
