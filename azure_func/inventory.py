"""Shared view on the inventory document for the output generators.

Besides walking ``data['Objects']`` this module works out how resources relate
to each other, without knowing anything about individual resource types:

* containment - a resource id that extends another resource id is a child of
  it (``.../servers/sql1/databases/db1`` belongs to ``.../servers/sql1``);
* references - any property value that is the id of another known resource is
  a relationship (a VM pointing at its NIC, a private endpoint at its target).
"""
import re

RESOURCE_ID_RE = re.compile(r"^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/[^/]+/[^/]+/[^/]+", re.I)


def iter_details(data):
    """Yield ``(subscription_id, resource_group, entry, detail)`` for every resource.

    ``Details`` is normally a dict. Lists (written by older versions of the
    tool) and error placeholders are handled so old output.json files still load.
    """
    for subscription_id, groups in (data.get("Objects") or {}).items():
        for rg_name, entries in (groups or {}).items():
            for entry in entries or []:
                details = entry.get("Details")
                if isinstance(details, dict):
                    details = [details]
                for detail in details or []:
                    if isinstance(detail, dict) and "Error" not in detail and detail.get("id"):
                        yield subscription_id, rg_name, entry, detail


def parent_resource_id(resource_id):
    """Id of the resource one level up, or None for a top-level resource."""
    parts = resource_id.split("/")
    providers = [index for index, part in enumerate(parts) if part.lower() == "providers"]
    if not providers:
        return None
    last = providers[-1]
    if len(parts) - (last + 2) > 2:  # more than one type/name pair after the namespace
        return "/".join(parts[:-2])
    if len(providers) > 1:  # extension resource: its parent is the resource it extends
        return "/".join(parts[:last])
    return None


def short_name(resource_id):
    """Last segment of a resource id."""
    return resource_id.rstrip("/").rsplit("/", 1)[-1]


def type_of_id(resource_id):
    """Resource type encoded in a resource id, e.g. Microsoft.Network/virtualNetworks/subnets."""
    parts = resource_id.split("/")
    providers = [index for index, part in enumerate(parts) if part.lower() == "providers"]
    if not providers or providers[-1] + 1 >= len(parts):
        return ""
    tail = parts[providers[-1] + 1:]
    return "/".join([tail[0]] + tail[1::2])


class Node:
    """One resource plus its place in the containment/reference graph."""

    __slots__ = ("key", "id", "name", "type", "type_lower", "kind", "subscription_id", "resource_group",
                 "location", "detail", "recommendations", "parent", "children", "refs", "raw_refs")

    def __init__(self, subscription_id, rg_name, entry, detail):
        self.id = detail["id"]
        self.key = self.id.lower()
        self.name = str(detail.get("name") or short_name(self.id))
        self.type = detail.get("type") or entry.get("ResourceType") or type_of_id(self.id)
        self.type_lower = self.type.lower()
        self.kind = detail.get("kind") or ""
        self.subscription_id = subscription_id
        self.resource_group = rg_name
        self.location = detail.get("location") or ""
        self.detail = detail
        self.recommendations = entry.get("Recommendations") or []
        self.parent = None      # Node this resource is contained in (by id)
        self.children = []      # Nodes contained in this resource
        self.refs = {}          # key of referenced node -> property path of the reference
        self.raw_refs = []      # every (lower-case resource id, property path) found

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def __repr__(self):
        return f"<Node {self.type} {self.name}>"


class Inventory:
    """All resources of an inventory document, indexed and linked."""

    def __init__(self, data):
        self.data = data
        self.nodes = {}
        for subscription_id, rg_name, entry, detail in iter_details(data):
            node = Node(subscription_id, rg_name, entry, detail)
            self.nodes.setdefault(node.key, node)
        self._link_hierarchy()
        self._link_references()

    # -- lookups -----------------------------------------------------------
    def get(self, resource_id):
        return self.nodes.get((resource_id or "").lower())

    def resolve(self, resource_id):
        """The node for an id, or for its nearest known ancestor (a subnet id
        resolves to its virtual network when subnets are not in the inventory)."""
        current = (resource_id or "").lower()
        while current:
            node = self.nodes.get(current)
            if node is not None:
                return node
            current = parent_resource_id(current)
        return None

    def subscription_name(self, subscription_id):
        info = (self.data.get("Subscriptions") or {}).get(subscription_id) or {}
        return info.get("displayName") or subscription_id

    # -- graph construction ------------------------------------------------
    def _link_hierarchy(self):
        for node in self.nodes.values():
            parent_id = parent_resource_id(node.key)
            while parent_id:
                parent = self.nodes.get(parent_id)
                if parent is not None:
                    node.parent = parent
                    parent.children.append(node)
                    break
                parent_id = parent_resource_id(parent_id)

    def _link_references(self):
        for node in self.nodes.values():
            self._scan(node, node.detail, "", top=True)
            related = {ancestor.key for ancestor in node.ancestors()}
            for ref, path in node.raw_refs:
                target = self.resolve(ref)
                if target is None or target is node or target.key in related:
                    continue
                if any(ancestor is node for ancestor in target.ancestors()):
                    continue  # pointing at something inside itself
                node.refs.setdefault(target.key, path)

    def _scan(self, node, value, path, top=False):
        if isinstance(value, dict):
            own_id = value.get("id")
            if not top and isinstance(own_id, str) and RESOURCE_ID_RE.match(own_id):
                node.raw_refs.append((own_id.lower(), path))
                if own_id.lower() != node.key and own_id.lower() in self.nodes:
                    return  # a full copy of another resource; that resource has its own node
            for key, child in value.items():
                if key == "id" and isinstance(child, str):
                    continue
                if isinstance(key, str) and key.startswith("/") and RESOURCE_ID_RE.match(key):
                    node.raw_refs.append((key.lower(), path))  # e.g. identity.userAssignedIdentities
                self._scan(node, child, f"{path}.{key}" if path else str(key))
        elif isinstance(value, list):
            for child in value:
                self._scan(node, child, f"{path}[]")
        elif isinstance(value, str) and value.startswith("/") and RESOURCE_ID_RE.match(value):
            node.raw_refs.append((value.lower(), path))
