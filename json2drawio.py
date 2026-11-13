"""draw.io (diagrams.net) output.

The file contains one page per subscription plus a network topology page:

* **Subscription pages** - subscription > resource groups > resources, drawn
  with the official Azure icons. Resources that belong together (a VM with its
  NIC, disks and extensions, a SQL server with its databases, an App Service
  plan with its apps) are boxed together. Every other relationship found in
  the resource properties becomes a link on a toggleable layer.
* **Network topology** - virtual networks > subnets > whatever is deployed
  into them, plus peerings, gateway connections and private endpoint targets.

Each shape carries the resource's key properties (hover, or Edit Data) and a
link to the resource in the Azure portal.

Everything is derived generically from resource ids and properties, so
resource types this tool has never heard of are drawn and linked as well.

Can also be run on its own:  python json2drawio.py output.json output.drawio
"""
import datetime
import html
import ipaddress
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

from azure_func.icons import CATEGORY_ORDER, category_of, describe, drawio_image
from azure_func.inventory import Inventory, RESOURCE_ID_RE, short_name, type_of_id

# ---------------------------------------------------------------------------
# Resource types with a special role in the diagrams (all lower case)
# ---------------------------------------------------------------------------
VNET = "microsoft.network/virtualnetworks"
SUBNET = "microsoft.network/virtualnetworks/subnets"
PEERING = "microsoft.network/virtualnetworks/virtualnetworkpeerings"
NIC = "microsoft.network/networkinterfaces"
PUBLIC_IP = "microsoft.network/publicipaddresses"
PRIVATE_ENDPOINT = "microsoft.network/privateendpoints"
DNS_LINK = "microsoft.network/privatednszones/virtualnetworklinks"
PRIVATE_DNS_ZONE = "microsoft.network/privatednszones"
CONNECTION = "microsoft.network/connections"
VM = "microsoft.compute/virtualmachines"

# A resource of the first type is drawn inside the box of a related resource
# of one of the second types (when both live in the same resource group).
ATTACH_RULES = [
    (NIC, {VM, PRIVATE_ENDPOINT}),
    ("microsoft.compute/disks", {VM}),
    (PUBLIC_IP, {NIC, VM, "microsoft.network/loadbalancers", "microsoft.network/applicationgateways",
                 "microsoft.network/bastionhosts", "microsoft.network/azurefirewalls",
                 "microsoft.network/virtualnetworkgateways", "microsoft.network/natgateways"}),
    ("microsoft.web/sites", {"microsoft.web/serverfarms"}),
    ("microsoft.app/containerapps", {"microsoft.app/managedenvironments"}),
    ("microsoft.app/jobs", {"microsoft.app/managedenvironments"}),
    ("microsoft.alertsmanagement/smartdetectoralertrules", {"microsoft.insights/components"}),
    ("microsoft.devtestlab/schedules", {VM}),
    ("microsoft.network/applicationgatewaywebapplicationfirewallpolicies", {"microsoft.network/applicationgateways"}),
    ("microsoft.network/firewallpolicies", {"microsoft.network/azurefirewalls"}),
    (CONNECTION, {"microsoft.network/virtualnetworkgateways"}),
]

# Not drawn as shapes on the subscription pages (the network page shows them).
HIDDEN_ON_RESOURCE_PAGES = {PEERING, DNS_LINK}
# Links to a virtual network are only drawn for these; "X is deployed in
# subnet Y" is what the network page is for.
VNET_ASSOCIATIONS = {VNET, SUBNET, "microsoft.network/networksecuritygroups", "microsoft.network/routetables",
                     "microsoft.network/natgateways", "microsoft.network/serviceendpointpolicies",
                     "microsoft.network/ddosprotectionplans"}
# Never placed inside a subnet on the network page.
NOT_PLACED_IN_SUBNETS = {VNET, SUBNET, PEERING, DNS_LINK, PRIVATE_DNS_ZONE, PUBLIC_IP,
                         "microsoft.network/networksecuritygroups", "microsoft.network/routetables",
                         "microsoft.network/natgateways", "microsoft.network/serviceendpointpolicies",
                         "microsoft.network/ddosprotectionplans", "microsoft.network/networkwatchers"}

SUBNET_ID_RE = re.compile(r"^(/subscriptions/[^/]+/resourcegroups/[^/]+/providers/microsoft\.network/"
                          r"virtualnetworks/[^/]+)/subnets/[^/]+", re.I)
GUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)

# ---------------------------------------------------------------------------
# Look and feel
# ---------------------------------------------------------------------------
SLOT_W, SLOT_H, ICON = 128, 100, 48                  # a resource
CHILD_W, CHILD_H, CHILD_ICON = 106, 84, 32           # a resource inside a cluster
GAP, PAD = 12, 14
MAX_CLUSTER_CHILDREN = 14
TEXT, MUTED = "#1F2328", "#57606A"
ZWSP = "\u200b"

LINKS = {  # category -> (layer name, colour, dashed)
    "network": ("Links - network", "#0969DA", False),
    "data": ("Links - data & storage", "#1A7F37", False),
    "security": ("Links - identity & security", "#8250DF", True),
    "monitoring": ("Links - monitoring", "#BC4C00", True),
    "other": ("Links - other", "#6E7781", False),
}
NETWORK_LINKS = {  # kind -> (layer name, colour, dashed, width)
    "peering": ("VNet peering", "#0969DA", False, 2),
    "privatelink": ("Private Link", "#8250DF", True, 1),
    "gateway": ("Gateway connection", "#1A7F37", True, 2),
    "other": ("Other links", "#6E7781", False, 1),
}
IMPACT_COLORS = {"high": "#CF222E", "medium": "#BC4C00", "low": "#0969DA"}


_icon_mode = "embedded"  # set per run by build_drawio()


def _image_style(icon_stem, size):
    image, width, height = drawio_image(icon_stem, _icon_mode, size)
    return _style(image=image or None, imageWidth=width, imageHeight=height)


def _text_width(text, size, bold=False):
    return len(text) * size * (0.62 if bold else 0.56)


def _fit(text, per_line, max_lines):
    """Shorten text to what fits and add break opportunities for long words."""
    limit = per_line * max_lines - 1
    if len(text) > limit:
        tail = max(4, per_line // 3)
        text = text[:limit - tail - 1] + "\u2026" + text[-tail:]
    out, run = [], 0
    for char in text:
        out.append(char)
        run += 1
        if char in "-_./;:":
            out.append(ZWSP)
            run = 0
        elif char == " ":
            run = 0
        elif run >= per_line - 1:
            out.append(ZWSP)
            run = 0
    return "".join(out)


def _style(**entries):
    return "".join(f"{key}={value};" for key, value in entries.items() if value is not None)


def _resource_style(icon_stem, icon=ICON, font=10):
    return ("shape=label;html=1;whiteSpace=wrap;overflow=hidden;fillColor=none;strokeColor=none;"
            "imageAlign=center;imageVerticalAlign=top;spacing=0;verticalAlign=top;align=center;"
            + _image_style(icon_stem, icon)
            + _style(spacingTop=icon + 8, fontSize=font, fontColor=TEXT))


def _container_style(icon_stem, fill, stroke, dashed=False, font=12, icon=22, stroke_width=1, arc=10):
    return ("shape=label;html=1;whiteSpace=wrap;container=1;collapsible=0;recursiveResize=0;rounded=1;"
            "absoluteArcSize=1;imageAlign=left;imageVerticalAlign=top;align=left;verticalAlign=top;"
            "spacing=5;fontStyle=1;"
            + _image_style(icon_stem, icon)
            + _style(arcSize=arc, fillColor=fill, strokeColor=stroke, strokeWidth=stroke_width,
                     dashed=1 if dashed else None, dashPattern="6 4" if dashed else None,
                     spacingLeft=icon + 10, spacingTop=max(0, (icon - font) // 2 - 1),
                     fontSize=font, fontColor=TEXT))


def _subtitle(text, size=10):
    return f'<br><span style="font-weight:normal;font-size:{size}px;color:{MUTED}">{html.escape(text)}</span>'


# ---------------------------------------------------------------------------
# draw.io document model
# ---------------------------------------------------------------------------
class Page:
    """One page (``<diagram>``) of the draw.io file."""

    def __init__(self, name, index):
        self.name = name
        self.id = f"page-{index}"
        self._prefix = f"p{index}-"
        self._count = 1
        self._root = ET.Element("root")
        ET.SubElement(self._root, "mxCell", {"id": f"{self._prefix}0"})
        ET.SubElement(self._root, "mxCell", {"id": f"{self._prefix}1", "parent": f"{self._prefix}0",
                                              "value": "Resources"})
        self.base_layer = f"{self._prefix}1"
        self.cell_of = {}  # node key -> cell id
        self.layers = {}   # layer name -> cell id

    def _new_id(self):
        self._count += 1
        return f"{self._prefix}{self._count}"

    def layer(self, name, visible=True):
        cell_id = self._new_id()
        attributes = {"id": cell_id, "parent": f"{self._prefix}0", "value": name}
        if not visible:
            attributes["visible"] = "0"
        ET.SubElement(self._root, "mxCell", attributes)
        return cell_id

    def named_layer(self, name):
        """A layer created on first use (later layers are drawn on top)."""
        if name not in self.layers:
            self.layers[name] = self.layer(name)
        return self.layers[name]

    def _cell(self, label, attributes, data):
        cell_id = self._new_id()
        if data:
            wrapper = ET.SubElement(self._root, "object", {"label": label, "id": cell_id})
            for key, value in data.items():
                if value not in (None, ""):
                    wrapper.set(key, str(value))
            cell = ET.SubElement(wrapper, "mxCell", attributes)
        else:
            cell = ET.SubElement(self._root, "mxCell", {"id": cell_id, "value": label, **attributes})
        return cell_id, cell

    def vertex(self, label, style, x, y, width, height, parent=None, data=None):
        cell_id, cell = self._cell(label, {"style": style, "vertex": "1", "parent": parent or self.base_layer}, data)
        ET.SubElement(cell, "mxGeometry", {"x": str(round(x)), "y": str(round(y)), "width": str(round(width)),
                                           "height": str(round(height)), "as": "geometry"})
        return cell_id

    def edge(self, source, target, style, parent=None, label="", data=None):
        attributes = {"style": style, "edge": "1", "parent": parent or self.base_layer,
                      "source": source, "target": target}
        cell_id, cell = self._cell(label, attributes, data)
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        return cell_id

    def line(self, x1, y1, x2, y2, style, parent):
        """An unconnected line (used for the legend)."""
        cell_id, cell = self._cell("", {"style": style, "edge": "1", "parent": parent}, None)
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        ET.SubElement(geometry, "mxPoint", {"x": str(x1), "y": str(y1), "as": "sourcePoint"})
        ET.SubElement(geometry, "mxPoint", {"x": str(x2), "y": str(y2), "as": "targetPoint"})
        return cell_id

    def to_xml(self):
        diagram = ET.Element("diagram", {"id": self.id, "name": self.name})
        model = ET.SubElement(diagram, "mxGraphModel", {
            "dx": "1600", "dy": "900", "grid": "0", "gridSize": "10", "guides": "1", "tooltips": "1",
            "connect": "1", "arrows": "1", "fold": "1", "page": "0", "pageScale": "1", "pageWidth": "1654",
            "pageHeight": "1169", "math": "0", "shadow": "0", "background": "#FFFFFF"})
        model.append(self._root)
        return diagram


# ---------------------------------------------------------------------------
# Layout: boxes that know their size and how to draw themselves
# ---------------------------------------------------------------------------
class Leaf:
    def __init__(self, width, height, draw):
        self.w, self.h, self._draw = width, height, draw

    def emit(self, page, parent, x, y):
        return self._draw(page, parent, x, y)


def _flow(boxes, max_width, gap=GAP):
    """Place boxes left to right, wrapping rows. Returns (positions, width, height)."""
    positions, x, y, row_height, width = [], 0, 0, 0, 0
    for box in boxes:
        if x > 0 and x + box.w > max_width:
            x, y, row_height = 0, y + row_height + gap, 0
        positions.append((x, y))
        x += box.w + gap
        row_height = max(row_height, box.h)
        width = max(width, x - gap)
    return positions, width, y + row_height


def _ideal_width(boxes, aspect=1.6, gap=GAP):
    """Row width that packs the boxes into roughly the given aspect ratio."""
    if not boxes:
        return 0
    area = sum((box.w + gap) * (box.h + gap) for box in boxes)
    return max(max(box.w for box in boxes), math.sqrt(area * aspect))


class Container:
    """A titled box holding other boxes."""

    def __init__(self, label, style, children, header=40, min_width=0, aspect=1.6, data=None, gap=GAP,
                 key=None, max_width=None, justify=False):
        self.label, self.style, self.children, self.data, self.key = label, style, children, data, key
        self.header = header
        target = max_width or _ideal_width(children, aspect, gap)
        self.positions, inner_width, inner_height = _flow(children, max(target, min_width - 2 * PAD), gap)
        self.w = max(inner_width + 2 * PAD, min_width)
        if justify:
            self._justify(self.w - 2 * PAD, gap)
        self.h = header + inner_height + (PAD if children else 4)

    def _justify(self, inner_width, gap):
        """Widen the boxes of every row so all rows end at the same right edge."""
        rows = defaultdict(list)
        for index, (_, y) in enumerate(self.positions):
            rows[y].append(index)
        for y, indexes in rows.items():
            used = sum(self.children[i].w for i in indexes) + gap * (len(indexes) - 1)
            extra, x = max(0, inner_width - used) / len(indexes), 0
            for i in indexes:
                self.children[i].w += extra
                self.positions[i] = (x, y)
                x += self.children[i].w + gap

    def emit(self, page, parent, x, y):
        cell = page.vertex(self.label, self.style, x, y, self.w, self.h, parent, self.data)
        if self.key:
            page.cell_of[self.key] = cell
        for child, (child_x, child_y) in zip(self.children, self.positions):
            child.emit(page, cell, PAD + child_x, self.header + child_y)
        return cell


# ---------------------------------------------------------------------------
# What the diagrams know about the inventory
# ---------------------------------------------------------------------------
class Model:
    """The inventory plus the grouping decisions shared by all pages."""

    def __init__(self, data):
        self.data = data
        self.inventory = Inventory(data)
        self.nodes = self.inventory.nodes
        self.incoming = defaultdict(list)
        for node in self.nodes.values():
            for target in node.refs:
                self.incoming[target].append(node)
        self._attached = {}
        self._attach()
        self.members = defaultdict(list)  # cluster parent key -> child nodes
        for node in self.nodes.values():
            parent = self.cluster_parent(node)
            if parent is not None:
                self.members[parent.key].append(node)

    def _attach(self):
        rules = defaultdict(set)
        for child_type, parent_types in ATTACH_RULES:
            rules[child_type] |= parent_types
        for node in self.nodes.values():
            allowed = rules.get(node.type_lower)
            if not allowed or node.parent is not None:
                continue
            related = [self.nodes[key] for key in node.refs] + self.incoming.get(node.key, [])
            candidates = sorted(
                (other for other in related
                 if other.type_lower in allowed and other.subscription_id == node.subscription_id
                 and other.resource_group == node.resource_group),
                key=lambda other: other.key)
            if candidates:
                self._attached[node.key] = candidates[0]

    def cluster_parent(self, node):
        """The resource this one is drawn inside of, if any."""
        return node.parent if node.parent is not None else self._attached.get(node.key)

    def cluster_chain(self, node):
        chain, current = [], self.cluster_parent(node)
        while current is not None and current not in chain:
            chain.append(current)
            current = self.cluster_parent(current)
        return chain

    def descendants(self, node):
        result = []
        for child in sorted(self.members.get(node.key, []), key=sort_key):
            result.append(child)
            result.extend(self.descendants(child))
        return result

    def network_owner(self, node):
        """The resource shown on the network page for ``node``: a NIC is shown
        as its VM or private endpoint, a child resource as its parent."""
        current, seen = node, set()
        while current.key not in seen:
            seen.add(current.key)
            if current.parent is not None:
                current = current.parent
            elif current.type_lower == NIC and current.key in self._attached:
                current = self._attached[current.key]
            else:
                break
        return current

    def subscription_name(self, subscription_id):
        return self.inventory.subscription_name(subscription_id)

    def portal_link(self, node):
        tenant = ((self.data.get("Subscriptions") or {}).get(node.subscription_id) or {}).get("tenantId")
        return f"https://portal.azure.com/#@{tenant or ''}/resource{node.id}"


def sort_key(node):
    category = category_of(node.type)
    order = CATEGORY_ORDER.index(category) if category in CATEGORY_ORDER else len(CATEGORY_ORDER)
    return order, node.type_lower, node.name.lower()


def display_name(node):
    properties = node.detail.get("properties") or {}
    name = node.name.rsplit("/", 1)[-1]
    if ";" in name and properties.get("friendlyName"):
        return str(properties["friendlyName"])
    if GUID_RE.match(name) and properties.get("displayName"):
        return str(properties["displayName"])
    return name


def _sku_text(detail):
    sku = detail.get("sku") or (detail.get("properties") or {}).get("sku")
    if isinstance(sku, dict):
        parts = [str(sku[key]) for key in ("name", "tier", "capacity") if sku.get(key) not in (None, "")]
        return " / ".join(dict.fromkeys(parts))
    return str(sku) if sku else ""


def _safe_attribute(name):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    return cleaned if re.match(r"^[A-Za-z_]", cleaned) else f"_{cleaned}"


def node_data(model, node, extra=None):
    """Shape data shown by draw.io on hover and under Edit Data."""
    icon, type_name = _describe(node)
    properties = node.detail.get("properties") or {}
    data = {
        "name": display_name(node),
        "type": node.type,
        "typeName": type_name,
        "resourceGroup": node.resource_group,
        "subscription": model.subscription_name(node.subscription_id),
        "location": node.location,
        "kind": node.kind,
        "sku": _sku_text(node.detail),
        "state": properties.get("provisioningState") or properties.get("state") or properties.get("status"),
        "zones": ", ".join(str(zone) for zone in node.detail.get("zones") or []),
        "resourceId": node.id,
        "tags": category_of(node.type),          # draw.io tags: show or hide shapes per category
        "link": model.portal_link(node),
    }
    if node.recommendations:
        data["advisor"] = f"{len(node.recommendations)} recommendation(s)"
    data.update(extra or {})
    for key, value in (node.detail.get("tags") or {}).items():
        data.setdefault(_safe_attribute(f"tag_{key}"), value)
    return data


def _describe(node):
    sku = node.detail.get("sku")
    return describe(node.type, node.kind, sku.get("name", "") if isinstance(sku, dict) else "")


def _label(name, type_name, per_line, max_lines, small, extra=None):
    text = f"<b>{html.escape(_fit(name, per_line, max_lines))}</b>"
    for line in [type_name] + list(extra or []):
        if line:
            text += f'<br><font color="{MUTED}" style="font-size:{small}px">{html.escape(line)}</font>'
    return text


def resource_leaf(model, node, small=False, extra_lines=None, extra_data=None):
    """A Leaf that draws one resource (icon, name, type, Advisor badge)."""
    icon_stem, type_name = _describe(node)
    width, height, icon, font = (CHILD_W, CHILD_H, CHILD_ICON, 9) if small else (SLOT_W, SLOT_H, ICON, 10)
    extra_lines = [line for line in extra_lines or [] if line]
    height += (font + 2) * len(extra_lines)
    per_line = int((width - 8) / (font * 0.56))
    label = _label(display_name(node), type_name, per_line, 2, font - 1, extra_lines)
    style = _resource_style(icon_stem, icon, font)
    data = node_data(model, node, extra_data)

    def draw(page, parent, x, y):
        cell = page.vertex(label, style, x, y, width, height, parent, data)
        page.cell_of.setdefault(node.key, cell)
        if node.recommendations:
            _advisor_badge(page, parent, node, x + width / 2 + icon / 2 - 5, y + 1)
        return cell

    return Leaf(width, height, draw)


def _advisor_badge(page, parent, node, x, y):
    impacts = [str((rec.get("properties") or rec).get("impact", "")).lower() for rec in node.recommendations]
    color = next((IMPACT_COLORS[level] for level in ("high", "medium", "low") if level in impacts), "#6E7781")
    data = {"tooltip": "Azure Advisor:\n" + "\n".join(_recommendation_text(rec) for rec in node.recommendations)}
    style = ("ellipse;html=1;aspect=fixed;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=9;fontStyle=1;"
             f"fillColor={color};connectable=0;")
    page.vertex(str(len(node.recommendations)), style, x, y, 16, 16, parent, data)


def _recommendation_text(recommendation):
    properties = recommendation.get("properties") or recommendation
    short = properties.get("shortDescription") or properties.get("short_description") or {}
    return f"[{properties.get('impact', '?')} / {properties.get('category', '?')}] {short.get('problem', '')}"


def _note(text, width=CHILD_W, height=CHILD_H):
    style = f"text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=10;fontColor={MUTED};"
    return Leaf(width, height, lambda page, parent, x, y: page.vertex(html.escape(text), style, x, y, width,
                                                                       height, parent))


# ---------------------------------------------------------------------------
# Subscription pages
# ---------------------------------------------------------------------------
def _cluster(model, root, hidden):
    """A resource together with everything drawn inside its box."""
    members = [node for node in model.descendants(root) if node.type_lower not in hidden]
    if not members:
        return resource_leaf(model, root)
    shown = members[:MAX_CLUSTER_CHILDREN]
    children = [resource_leaf(model, node, small=True) for node in shown]
    if len(members) > len(shown):
        children.append(_note(f"+{len(members) - len(shown)} more"))
    columns = min(len(children), max(2, math.ceil(math.sqrt(len(children) * 2))))
    grid_width = columns * CHILD_W + (columns - 1) * 6
    positions, grid_width, grid_height = _flow(children, grid_width, 6)
    root_leaf = resource_leaf(model, root)
    width = PAD + SLOT_W + 8 + grid_width + PAD
    height = max(SLOT_H, grid_height) + 2 * 10
    style = "rounded=1;absoluteArcSize=1;arcSize=10;html=1;container=1;collapsible=0;recursiveResize=0;" \
            "fillColor=#F6F8FA;strokeColor=#D0D7DE;connectable=0;"

    def draw(page, parent, x, y):
        box = page.vertex("", style, x, y, width, height, parent)
        root_leaf.emit(page, box, PAD - 4, 10)
        # a hairline between the main resource and its parts
        page.line(PAD + SLOT_W, 14, PAD + SLOT_W, height - 14,
                  "endArrow=none;html=1;strokeColor=#D0D7DE;strokeWidth=1;", box)
        for child, (child_x, child_y) in zip(children, positions):
            child.emit(page, box, PAD + SLOT_W + 8 + child_x, 10 + child_y)
        return box

    return Leaf(width, height, draw)


def _resource_group_box(model, subscription_id, rg_name, nodes):
    visible = [node for node in nodes if node.type_lower not in HIDDEN_ON_RESOURCE_PAGES]
    visible_keys = {node.key for node in visible}
    roots = sorted((node for node in visible if model.cluster_parent(node) is None
                    or model.cluster_parent(node).key not in visible_keys), key=sort_key)
    boxes = [_cluster(model, root, HIDDEN_ON_RESOURCE_PAGES) for root in roots]
    # Clusters first, single resources after: keeps rows tidy.
    boxes.sort(key=lambda box: 0 if box.w > SLOT_W else 1)
    meta = ((model.data.get("ResourceGroups") or {}).get(subscription_id) or {}).get(rg_name) or {}
    subtitle = " \u00b7 ".join(part for part in (meta.get("location"), f"{len(visible)} resources") if part)
    label = html.escape(rg_name) + _subtitle(subtitle)
    data = {"name": rg_name, "type": "Microsoft.Resources/resourceGroups", "location": meta.get("location"),
            "resourceId": meta.get("id"), "resources": len(visible)}
    for key, value in (meta.get("tags") or {}).items():
        data.setdefault(_safe_attribute(f"tag_{key}"), value)
    if not boxes:
        boxes = [_note("no resources", 110, 24)]
    min_width = max(_text_width(rg_name, 12, True), _text_width(subtitle, 10)) + 60
    return Container(label, _container_style("Resource-Groups", "#FFFFFF", "#8C959F", dashed=True),
                     boxes, header=46, min_width=min_width, data=data)


def _link_category(source, target):
    categories = {category_of(source.type), category_of(target.type)}
    for name in ("monitoring", "security", "network"):
        if name in categories:
            return name
    return "data" if categories & {"data", "storage"} else "other"


def _edge_style(color, dashed=False, width=1, arrows="single"):
    return ("html=1;rounded=0;endSize=5;startSize=5;"
            + _style(endArrow="open" if arrows != "none" else "none",
                     startArrow="open" if arrows == "both" else "none",
                     strokeColor=color, strokeWidth=width, dashed=1 if dashed else None,
                     opacity=55, fontSize=9, fontColor=color, labelBackgroundColor="#FFFFFF"))


def _resource_links(model, page, nodes):
    """Draw every relationship between resources on this page."""
    on_page = {node.key for node in nodes}

    def shown(node):
        while node is not None and node.type_lower in HIDDEN_ON_RESOURCE_PAGES:
            node = node.parent
        return node

    layers, seen, counts = {}, set(), defaultdict(int)
    for node in sorted(nodes, key=lambda n: n.key):
        for target_key, path in node.refs.items():
            source, target = shown(node), shown(model.nodes[target_key])
            if source is None or target is None or source is target or target.key not in on_page:
                continue
            if source in model.cluster_chain(target) or target in model.cluster_chain(source):
                continue  # already expressed by drawing one inside the other
            vnet_side = {source.type_lower, target.type_lower} & {VNET, SUBNET}
            if vnet_side and not {source.type_lower, target.type_lower} <= VNET_ASSOCIATIONS:
                continue  # placement in a network: see the network page
            pair = frozenset((source.key, target.key))
            if pair in seen or source.key not in page.cell_of or target.key not in page.cell_of:
                continue
            seen.add(pair)
            category = _link_category(source, target)
            layer_name, color, dashed = LINKS[category]
            if category not in layers:
                layers[category] = page.layer(layer_name)
            counts[category] += 1
            page.edge(page.cell_of[source.key], page.cell_of[target.key], _edge_style(color, dashed),
                      layers[category],
                      data={"from": display_name(source), "to": display_name(target), "via": path,
                            "tags": f"link {category}"})
    return counts


def _legend(page, x, y, entries, title="Links (toggle under View > Layers)"):
    """entries: [(text, colour, dashed)]"""
    height = 30 + 18 * len(entries)
    width = max([_text_width(title, 10, True)] + [_text_width(text, 10) + 50 for text, _, _ in entries]) + 24
    box = page.vertex(html.escape(title), "rounded=1;absoluteArcSize=1;arcSize=8;html=1;container=1;collapsible=0;"
                      f"fillColor=#FFFFFF;strokeColor=#D0D7DE;align=left;verticalAlign=top;spacingLeft=8;"
                      f"spacingTop=2;fontSize=10;fontStyle=1;fontColor={TEXT};connectable=0;", x, y, width, height)
    for index, (text, color, dashed) in enumerate(entries):
        row = 32 + 18 * index
        page.line(10, row, 44, row, _edge_style(color, dashed, 2), box)
        page.vertex(html.escape(text), f"text;html=1;align=left;verticalAlign=middle;fontSize=10;fontColor={TEXT};"
                    "connectable=0;", 50, row - 9, width - 56, 18, box)
    return width, height


def _title(page, title, subtitle):
    width = max(_text_width(title, 20, True), _text_width(subtitle, 11)) + 20
    page.vertex(f'<b style="font-size:20px">{html.escape(title)}</b>'
                f'<br><span style="font-size:11px;color:{MUTED}">{html.escape(subtitle)}</span>',
                f"text;html=1;align=left;verticalAlign=top;fontColor={TEXT};connectable=0;", 0, 0, width, 54)
    return width


def _generated(model):
    stamp = str((model.data.get("Properties") or {}).get("Datestamp") or datetime.datetime.now())[:16]
    return f"Generated {stamp} by Cloud-Infra-Visualization"


def build_subscription_page(model, subscription_id, index):
    name = model.subscription_name(subscription_id)
    page = Page(name[:60], index)
    by_group = defaultdict(list)
    for node in model.nodes.values():
        if node.subscription_id == subscription_id:
            by_group[node.resource_group].append(node)
    group_names = list(((model.data.get("Objects") or {}).get(subscription_id) or {}).keys())
    boxes = [_resource_group_box(model, subscription_id, rg_name, by_group.get(rg_name, []))
             for rg_name in sorted(group_names, key=str.lower)]
    boxes.sort(key=lambda box: -box.h)  # tallest first packs best
    nodes = [node for group in by_group.values() for node in group]
    info = (model.data.get("Subscriptions") or {}).get(subscription_id) or {}
    label = html.escape(name) + _subtitle(f"Subscription {subscription_id}", 11)
    data = {"name": name, "type": "Microsoft.Resources/subscriptions", "subscriptionId": subscription_id,
            "tenantId": info.get("tenantId"), "state": info.get("state"), "resourceGroups": len(group_names),
            "resources": len(nodes),
            "link": f"https://portal.azure.com/#@{info.get('tenantId') or ''}/resource/subscriptions/{subscription_id}"}
    if not boxes:
        boxes = [_note("no resource groups", 140, 24)]
    subscription = Container(label, _container_style("Subscriptions", "#F6FAFF", "#0969DA", font=15, icon=28,
                                                     stroke_width=2, arc=14),
                             boxes, header=58, aspect=1.7, data=data, gap=18,
                             min_width=_text_width(name, 15, True) + 80, justify=len(group_names) > 0)
    title_width = _title(page, name, f"{_generated(model)} \u00b7 {len(group_names)} resource groups \u00b7 "
                                     f"{len(nodes)} resources")
    subscription.emit(page, page.base_layer, 0, 70)
    counts = _resource_links(model, page, nodes)
    entries = [(f"{LINKS[c][0].split(' - ')[1]} ({counts[c]})", LINKS[c][1], LINKS[c][2]) for c in LINKS if counts[c]]
    if entries:
        _legend(page, max(title_width + 40, subscription.w - 300), 0, entries)
    return page


# ---------------------------------------------------------------------------
# Network topology page
# ---------------------------------------------------------------------------
def _find_ids(value):
    """Every resource id that appears anywhere in a JSON value."""
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str) and key.startswith("/") and RESOURCE_ID_RE.match(key):
                yield key
            yield from _find_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from _find_ids(child)
    elif isinstance(value, str) and value.startswith("/") and RESOURCE_ID_RE.match(value):
        yield value


def _find_values(value, wanted):
    """All string values stored under the given key name, at any depth."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key == wanted and isinstance(child, str):
                yield child
            else:
                yield from _find_values(child, wanted)
    elif isinstance(value, list):
        for child in value:
            yield from _find_values(child, wanted)


def _prefix_key(prefix):
    try:
        network = ipaddress.ip_network(prefix, strict=False)
        return network.version, int(network.network_address), network.prefixlen
    except ValueError:
        return 9, 0, 0


def _subnet_prefix(subnet):
    properties = subnet.get("properties") or {}
    return properties.get("addressPrefix") or ", ".join(properties.get("addressPrefixes") or [])


class Network:
    """Works out what is deployed where."""

    def __init__(self, model):
        self.model = model
        nodes = model.nodes
        self.vnets = [node for node in nodes.values() if node.type_lower == VNET]
        self.subnets = {}                       # subnet id (lower) -> (vnet node, subnet dict)
        for vnet in self.vnets:
            for subnet in (vnet.detail.get("properties") or {}).get("subnets") or []:
                if isinstance(subnet, dict) and subnet.get("id"):
                    self.subnets[subnet["id"].lower()] = (vnet, subnet)
        self.placed = {}                        # owner key -> subnet id
        self.in_subnet = defaultdict(list)      # subnet id -> [owner nodes]
        self.dns_zones = defaultdict(set)       # vnet key -> private DNS zone names
        self.vnet_refs = defaultdict(set)       # owner key -> vnet keys it points at
        self._place()

    def _place_in(self, node, subnet_id):
        owner = self.model.network_owner(node)
        if owner.type_lower in NOT_PLACED_IN_SUBNETS or owner.key in self.placed:
            return
        self.placed[owner.key] = subnet_id
        self.in_subnet[subnet_id].append(owner)

    def _place(self):
        nodes = self.model.nodes
        vnet_keys = {vnet.key for vnet in self.vnets}
        for node in sorted(nodes.values(), key=lambda n: n.key):
            if node.type_lower in (VNET, SUBNET, PEERING):
                continue
            for ref, _ in node.raw_refs:
                match = SUBNET_ID_RE.match(ref)
                if match and match.group(0) in self.subnets:
                    self._place_in(node, match.group(0))
                elif ref in vnet_keys:
                    if node.type_lower == DNS_LINK and node.parent is not None:
                        self.dns_zones[ref].add(node.parent.name)
                    else:
                        self.vnet_refs[self.model.network_owner(node).key].add(ref)
        # The subnet's side of the story (covers resources that do not name their subnet).
        for subnet_id, (_, subnet) in self.subnets.items():
            for ref in _find_ids(subnet.get("properties") or {}):
                node = self.model.inventory.resolve(ref)
                if node is not None and node.type_lower not in (VNET, SUBNET, PEERING):
                    self._place_in(node, subnet_id)

    def addresses(self, owner):
        """(private IPs, public IPs) of a resource and what is attached to it."""
        members = [owner] + self.model.descendants(owner)
        private = list(dict.fromkeys(ip for member in members if member.type_lower != PUBLIC_IP
                                     for ip in _find_values(member.detail.get("properties") or {}, "privateIPAddress")))
        public = list(dict.fromkeys(
            str((member.detail.get("properties") or {}).get("ipAddress"))
            for member in members
            if member.type_lower == PUBLIC_IP and (member.detail.get("properties") or {}).get("ipAddress")))
        return private, public


def _address_line(private, public):
    parts = private[:2] + (["\u2026"] if len(private) > 2 else [])
    text = ", ".join(parts)
    if public:
        text = f"{text} | {public[0]}" if text else public[0]
    return text


def _network_leaf(model, network, node, extra_lines=None):
    private, public = network.addresses(node)
    lines = [_address_line(private, public)] + list(extra_lines or [])
    return resource_leaf(model, node, extra_lines=[line for line in lines if line],
                         extra_data={"privateIPs": ", ".join(private), "publicIPs": ", ".join(public)})


def _external_leaf(page_key, resource_id, small=False, extra_lines=None):
    """A placeholder for something referenced but not part of the inventory."""
    note = "outside this inventory"
    resource_type = type_of_id(resource_id)
    icon_stem, type_name = describe(resource_type)
    name = short_name(resource_id)
    width, height, icon, font = (CHILD_W, CHILD_H, CHILD_ICON, 9) if small else (SLOT_W, SLOT_H, ICON, 10)
    lines = [line for line in list(extra_lines or []) + [note] if line]
    height += (font + 2) * len(lines)
    label = _label(name, type_name, int((width - 8) / (font * 0.56)), 2, font - 1, lines)
    style = _resource_style(icon_stem, icon, font) + "opacity=55;"
    data = {"name": name, "type": resource_type, "resourceId": resource_id, "remark": note,
            "subscription": resource_id.split("/")[2] if resource_id.count("/") > 2 else ""}

    def draw(page, parent, x, y):
        cell = page.vertex(label, style, x, y, width, height, parent, data)
        page.cell_of.setdefault(page_key, cell)
        return cell

    return Leaf(width, height, draw)


def _private_link_targets(node):
    """[(target resource id, group ids)] of a private endpoint."""
    properties = node.detail.get("properties") or {}
    connections = (properties.get("privateLinkServiceConnections") or []) + \
                  (properties.get("manualPrivateLinkServiceConnections") or [])
    targets = []
    for connection in connections:
        details = (connection or {}).get("properties") or {}
        if details.get("privateLinkServiceId"):
            targets.append((details["privateLinkServiceId"], ", ".join(details.get("groupIds") or [])))
    return targets


def _private_endpoint_leaf(model, network, node):
    """A private endpoint drawn next to the service it exposes."""
    endpoint_leaf = _network_leaf(model, network, node)
    targets = _private_link_targets(node)
    if not targets:
        return endpoint_leaf
    target_id, groups = targets[0]
    target = model.inventory.resolve(target_id)
    if target is not None:
        target_leaf = resource_leaf(model, target, small=True, extra_lines=[groups],
                                    extra_data={"role": "private link target"})
    else:
        target_leaf = _external_leaf(target_id.lower(), target_id, small=True, extra_lines=[groups])
    gap = 26
    style = (_edge_style(NETWORK_LINKS["privatelink"][1], dashed=True)
             + _style(exitX=1, exitY=round(29 / endpoint_leaf.h, 2), entryX=0, entryY=round(29 / target_leaf.h, 2)))
    data = {"from": node.name, "to": short_name(target_id), "groupIds": groups,
            "targets": "; ".join(short_name(tid) for tid, _ in targets), "tags": "link privatelink"}

    def draw(page, parent, x, y):
        source_cell = endpoint_leaf.emit(page, parent, x, y)
        target_cell = target_leaf.emit(page, parent, x + endpoint_leaf.w + gap, y + 8)
        page.edge(source_cell, target_cell, style, page.named_layer(NETWORK_LINKS["privatelink"][0]), data=data)
        return source_cell

    return Leaf(endpoint_leaf.w + gap + target_leaf.w, max(endpoint_leaf.h, target_leaf.h + 8), draw)


def _subnet_box(model, network, subnet_id, subnet):
    properties = subnet.get("properties") or {}
    notes = []
    for label, key in (("NSG", "networkSecurityGroup"), ("Routes", "routeTable"), ("NAT", "natGateway")):
        if isinstance(properties.get(key), dict) and properties[key].get("id"):
            notes.append(f"{label}: {short_name(properties[key]['id'])}")
    delegations = [(d.get("properties") or {}).get("serviceName") for d in properties.get("delegations") or []
                   if isinstance(d, dict)]
    if any(delegations):
        notes.append("Delegated: " + ", ".join(d for d in delegations if d))
    owners = sorted(network.in_subnet.get(subnet_id, []), key=sort_key)
    children = [_private_endpoint_leaf(model, network, owner) if owner.type_lower == PRIVATE_ENDPOINT
                else _network_leaf(model, network, owner) for owner in owners]
    title = f"{subnet.get('name', short_name(subnet_id))}  {_subnet_prefix(subnet)}".strip()
    subtitle = " \u00b7 ".join(notes) or ("empty" if not children else "")
    label = html.escape(title) + (_subtitle(subtitle, 9) if subtitle else "")
    data = {"name": subnet.get("name"), "type": "Microsoft.Network/virtualNetworks/subnets",
            "addressPrefix": _subnet_prefix(subnet), "resourceId": subnet.get("id"), "resources": len(children),
            "tags": "network"}
    data.update({note.split(": ")[0].lower(): note.split(": ", 1)[1] for note in notes})
    min_width = max(_text_width(title, 11, True), _text_width(subtitle, 9)) + 56
    # Up to four resources side by side, more columns only for busy subnets.
    columns = min(len(children), max(4, math.ceil(math.sqrt(len(children) * 2.5)))) or 1
    max_width = columns * (max((child.w for child in children), default=SLOT_W) + GAP)
    return Container(label, _container_style("Subnet", "#FFFFFF", "#54AEFF", font=11, icon=18),
                     children, header=42, min_width=min_width, max_width=max_width, data=data, key=subnet_id)


def _vnet_box(model, network, vnet):
    properties = vnet.detail.get("properties") or {}
    prefixes = (properties.get("addressSpace") or {}).get("addressPrefixes") or []
    subnets = sorted(((subnet_id, subnet) for subnet_id, (owner, subnet) in network.subnets.items() if owner is vnet),
                     key=lambda item: (_prefix_key(_subnet_prefix(item[1]).split(",")[0]), item[0]))
    boxes = [_subnet_box(model, network, subnet_id, subnet) for subnet_id, subnet in subnets]
    justify = bool(boxes)
    if not boxes:
        boxes = [_note("no subnets", 110, 24)]
    details = [vnet.resource_group, vnet.location, model.subscription_name(vnet.subscription_id)]
    dns_servers = (properties.get("dhcpOptions") or {}).get("dnsServers") or []
    if dns_servers:
        details.append("DNS: " + ", ".join(dns_servers))
    zones = sorted(network.dns_zones.get(vnet.key, []))
    if zones:
        details.append(f"{len(zones)} private DNS zone{'s' if len(zones) != 1 else ''} linked")
    title = f"{vnet.name}  {', '.join(prefixes)}".strip()
    subtitle = " \u00b7 ".join(part for part in details if part)
    label = html.escape(title) + _subtitle(subtitle)
    data = node_data(model, vnet, {"addressSpace": ", ".join(prefixes), "dnsServers": ", ".join(dns_servers),
                                   "privateDnsZones": ", ".join(zones), "subnets": len(subnets)})
    min_width = max(_text_width(title, 13, True), _text_width(subtitle, 10)) + 70
    return Container(label, _container_style("Virtual-Networks", "#F1F8FF", "#0969DA", dashed=True, font=13,
                                             icon=26, stroke_width=2, arc=14),
                     boxes, header=52, min_width=min_width, aspect=2.4, data=data, key=vnet.key, gap=14,
                     justify=justify)


def build_network_page(model, index):
    network = Network(model)
    if not network.vnets:
        return None
    page = Page("Network topology", index)
    nodes = model.nodes
    links = []          # (source key, target key, kind, data)
    outside = {}        # key -> Leaf drawn in the lane below the virtual networks
    foreign_vnets = {}  # key -> Leaf for peered networks that are not in the inventory

    def endpoint(resource_id, extra_lines=None):
        """Key of the shape standing for a resource id; adds a lane shape when needed."""
        node = model.inventory.resolve(resource_id)
        if node is None:
            key = resource_id.lower()
            outside.setdefault(key, _external_leaf(key, resource_id, extra_lines=extra_lines))
            return key
        owner = model.network_owner(node)
        if owner.type_lower != VNET and owner.key not in network.placed:
            lines = list(extra_lines or [])
            properties = owner.detail.get("properties") or {}
            if owner.type_lower == "microsoft.network/localnetworkgateways":
                space = (properties.get("localNetworkAddressSpace") or {}).get("addressPrefixes") or []
                lines.insert(0, ", ".join([str(properties.get("gatewayIpAddress") or "")] + space[:2]).strip(", "))
            outside.setdefault(owner.key, _network_leaf(model, network, owner, lines))
        return owner.key

    # ---- peerings ------------------------------------------------------------
    peered = {}
    for vnet in sorted(network.vnets, key=lambda n: n.key):
        for peering in (vnet.detail.get("properties") or {}).get("virtualNetworkPeerings") or []:
            properties = (peering or {}).get("properties") or {}
            remote = (properties.get("remoteVirtualNetwork") or {}).get("id")
            if not remote:
                continue
            remote_node = model.inventory.get(remote)
            target = remote_node.key if remote_node is not None else remote.lower()
            if remote_node is None:
                foreign_vnets.setdefault(target, _external_leaf(target, remote))
            pair = frozenset((vnet.key, target))
            if pair in peered:
                peered[pair]["both"] = True
                continue
            flags = [flag for flag, key in (("gateway transit", "allowGatewayTransit"),
                                            ("uses remote gateway", "useRemoteGateways"),
                                            ("forwarded traffic", "allowForwardedTraffic")) if properties.get(key)]
            peered[pair] = {"source": vnet.key, "target": target, "both": False,
                            "state": properties.get("peeringState") or "",
                            "data": {"peering": peering.get("name"), "from": vnet.name, "to": short_name(remote),
                                     "state": properties.get("peeringState"), "options": ", ".join(flags),
                                     "tags": "link peering"}}
    for entry in peered.values():
        links.append((entry["source"], entry["target"], "peering-both" if entry["both"] else "peering",
                      "" if entry["state"] in ("", "Connected") else entry["state"], entry["data"]))

    # ---- gateway connections (site-to-site, ExpressRoute, VNet-to-VNet) --------
    for node in sorted(nodes.values(), key=lambda n: n.key):
        if node.type_lower != CONNECTION:
            continue
        properties = node.detail.get("properties") or {}
        first = (properties.get("virtualNetworkGateway1") or {}).get("id")
        second = next(((properties.get(key) or {}).get("id") for key in
                       ("virtualNetworkGateway2", "localNetworkGateway2", "peer")
                       if (properties.get(key) or {}).get("id")), None)
        if first and second:
            kind = properties.get("connectionType") or "connection"
            text = f"{node.name} ({kind})"
            links.append((endpoint(first), endpoint(second, [text]), "gateway", "",
                          {"connection": node.name, "connectionType": kind,
                           "status": properties.get("connectionStatus"), "tags": "link gateway"}))

    # ---- anything else that points at a virtual network (virtual hubs, ...) ----
    for owner_key, vnet_keys in sorted(network.vnet_refs.items()):
        owner = nodes[owner_key]
        if owner.key in network.placed or owner.type_lower in NOT_PLACED_IN_SUBNETS or owner.type_lower == CONNECTION:
            continue
        for vnet_key in sorted(vnet_keys):
            links.append((endpoint(owner.id), vnet_key, "other", "", {"from": owner.name, "tags": "link"}))

    # ---- layout: most-peered network (the hub) first ---------------------------
    degree = defaultdict(int)
    for entry in peered.values():
        degree[entry["source"]] += 1
        degree[entry["target"]] += 1
    vnets = sorted(network.vnets, key=lambda n: (-degree[n.key], model.subscription_name(n.subscription_id), n.name))
    boxes = [_vnet_box(model, network, vnet) for vnet in vnets]
    boxes += [foreign_vnets[key] for key in sorted(foreign_vnets)]
    positions, width, height = _flow(boxes, _ideal_width(boxes, 2.0, 70), 70)

    subscriptions = {vnet.subscription_id for vnet in network.vnets}
    title_width = _title(page, "Network topology",
                         f"{_generated(model)} \u00b7 {len(network.vnets)} virtual networks \u00b7 "
                         f"{len(network.subnets)} subnets \u00b7 {len(subscriptions)} subscription(s)")
    top = 84
    if outside:  # on-premises sites and the like sit above the networks, next to the hub
        ordered = [outside[key] for key in sorted(outside, key=lambda k: (k not in nodes, k))]
        lane = Container("External connectivity and linked services",
                         _container_style("Connections", "#FAFBFC", "#8C959F", dashed=True, font=12),
                         ordered, header=40, max_width=max(width - 2 * PAD, SLOT_W * 3), min_width=330)
        lane.emit(page, page.base_layer, 0, top)
        top += lane.h + 60
        width = max(width, lane.w)
    for box, (x, y) in zip(boxes, positions):
        box.emit(page, page.base_layer, x, top + y)

    # ---- links -----------------------------------------------------------------
    for source, target, kind, label, data in links:
        if source == target or source not in page.cell_of or target not in page.cell_of:
            continue
        layer_name, color, dashed, stroke = NETWORK_LINKS[kind.split("-")[0]]
        style = _edge_style(color, dashed, stroke, "both" if kind.endswith("-both") else "single") + "opacity=100;"
        if label:  # only abnormal states are spelled out, e.g. a disconnected peering
            style = style.replace(f"strokeColor={color}", "strokeColor=#CF222E").replace(
                f"fontColor={color}", "fontColor=#CF222E")
        page.edge(page.cell_of[source], page.cell_of[target], style, page.named_layer(layer_name),
                  html.escape(label), data)
    entries = [(name, color, dashed) for name, color, dashed, _ in NETWORK_LINKS.values() if name in page.layers]
    if entries:
        _legend(page, max(title_width + 40, width - 250), 0, entries)
    return page


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def build_drawio(data, icons="embedded"):
    """Return the draw.io document (an ElementTree) for an inventory.

    ``icons`` is 'embedded' (self-contained file) or 'library' (reference the
    Azure icons bundled with draw.io; much smaller files).
    """
    global _icon_mode  # noqa: PLW0603 - a per-run setting read by the style helpers
    _icon_mode = icons
    model = Model(data)
    pages = []
    network_page = build_network_page(model, len(pages) + 1)
    subscription_ids = list((data.get("Objects") or {}).keys())
    names_seen = defaultdict(int)
    for subscription_id in sorted(subscription_ids, key=lambda s: model.subscription_name(s).lower()):
        page = build_subscription_page(model, subscription_id, len(pages) + 2 if network_page else len(pages) + 1)
        names_seen[page.name] += 1
        if names_seen[page.name] > 1:
            page.name = f"{page.name} ({names_seen[page.name]})"
        pages.append(page)
    if network_page:
        pages.append(network_page)

    mxfile = ET.Element("mxfile", {
        "host": "Cloud-Infra-Visualization",
        "modified": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "agent": "Cloud-Infra-Visualization",
        "version": "24.7.17",
        "type": "device",
        "pages": str(max(len(pages), 1)),
    })
    if not pages:
        empty = Page("Azure", 1)
        _title(empty, "No resources found", _generated(model))
        pages.append(empty)
    for page in pages:
        mxfile.append(page.to_xml())
    return ET.ElementTree(mxfile)


def generate_drawio(data, output_path, icons="embedded"):
    """Write the draw.io file for an inventory document."""
    tree = build_drawio(data, icons)
    ET.indent(tree, space=" ")
    tree.write(output_path, encoding="utf-8", xml_declaration=False)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Usage: python json2drawio.py <output.json> <output.drawio> [embedded|library]")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as handle:
        generate_drawio(json.load(handle), sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else "embedded")
    print(f"Wrote {sys.argv[2]}")
