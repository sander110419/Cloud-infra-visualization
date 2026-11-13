"""Collects a complete inventory of Azure resources.

Strategy (``engine='auto'``):

1. Azure Resource Graph returns every resource of every type, including its
   full ``properties``, a thousand at a time.
2. The ARM resource listing is used as a completeness check; anything Resource
   Graph did not return is read individually with a generic ``GET``.
3. Interesting child resources that neither listing contains (queues, blob
   containers, subnets, ...) are added from ``CHILD_COLLECTIONS``.
4. Azure Advisor recommendations are fetched once per subscription and
   attached to the resources they apply to.

If Resource Graph is unavailable the collector falls back to ARM only
(``engine='arm'``), which is slower but needs nothing but Reader access.
"""
import datetime
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor

from azure_func.arm import (
    API_ADVISOR,
    API_RESOURCE_GRAPH,
    API_RESOURCES,
    API_SUBSCRIPTIONS,
    ArmError,
)
from azure_func.inventory import parent_resource_id

SCRIPT_VERSION = "0.2"
NO_RESOURCE_GROUP = "(no resource group)"
GRAPH_PAGE_SIZE = 1000

logger = logging.getLogger(__name__)

# Child resources that are not part of the subscription-wide resource listing.
# parent type (lower case) -> [(relative path, child type, fallback api-version, predicate)]
# The api-version is looked up in the provider catalog; the fallback is only
# used when the catalog has no entry for the child type.
CHILD_COLLECTIONS = {
    "microsoft.servicebus/namespaces": [
        ("queues", "Microsoft.ServiceBus/namespaces/queues", "2021-11-01", None),
        ("topics", "Microsoft.ServiceBus/namespaces/topics", "2021-11-01", None),
    ],
    "microsoft.eventhub/namespaces": [
        ("eventhubs", "Microsoft.EventHub/namespaces/eventhubs", "2021-11-01", None),
    ],
    "microsoft.storage/storageaccounts": [
        ("blobServices/default/containers", "Microsoft.Storage/storageAccounts/blobServices/containers", "2023-01-01", None),
        ("fileServices/default/shares", "Microsoft.Storage/storageAccounts/fileServices/shares", "2023-01-01", None),
        ("queueServices/default/queues", "Microsoft.Storage/storageAccounts/queueServices/queues", "2023-01-01", None),
        ("tableServices/default/tables", "Microsoft.Storage/storageAccounts/tableServices/tables", "2023-01-01", None),
    ],
    "microsoft.web/sites": [
        ("functions", "Microsoft.Web/sites/functions", "2022-03-01",
         lambda r: "functionapp" in (r.get("kind") or "").lower()),
    ],
    "microsoft.sql/managedinstances": [
        ("databases", "Microsoft.Sql/managedInstances/databases", "2021-11-01", None),
    ],
    "microsoft.documentdb/databaseaccounts": [
        ("sqlDatabases", "Microsoft.DocumentDB/databaseAccounts/sqlDatabases", "2023-04-15",
         lambda r: (r.get("kind") or "").lower() != "mongodb"),
        ("mongodbDatabases", "Microsoft.DocumentDB/databaseAccounts/mongodbDatabases", "2023-04-15",
         lambda r: (r.get("kind") or "").lower() == "mongodb"),
    ],
    "microsoft.dbforpostgresql/flexibleservers": [
        ("databases", "Microsoft.DBforPostgreSQL/flexibleServers/databases", "2022-12-01", None),
    ],
    "microsoft.dbformysql/flexibleservers": [
        ("databases", "Microsoft.DBforMySQL/flexibleServers/databases", "2021-05-01", None),
    ],
    "microsoft.recoveryservices/vaults": [
        ("backupProtectedItems", "Microsoft.RecoveryServices/vaults/backupProtectedItems", "2023-02-01", None),
    ],
    "microsoft.cdn/profiles": [
        ("afdEndpoints", "Microsoft.Cdn/profiles/afdEndpoints", "2023-05-01",
         lambda r: "frontdoor" in ((r.get("sku") or {}).get("name") or "").lower()),
        ("endpoints", "Microsoft.Cdn/profiles/endpoints", "2023-05-01",
         lambda r: "frontdoor" not in ((r.get("sku") or {}).get("name") or "").lower()),
    ],
    "microsoft.apimanagement/service": [
        ("apis", "Microsoft.ApiManagement/service/apis", "2022-08-01", None),
    ],
    "microsoft.network/virtualhubs": [
        ("hubVirtualNetworkConnections", "Microsoft.Network/virtualHubs/hubVirtualNetworkConnections", "2023-05-01", None),
    ],
}

# Child resources ARM already returns inside the parent's properties. They are
# promoted to resources of their own (no extra API calls needed).
EMBEDDED_CHILDREN = {
    "microsoft.network/virtualnetworks": [
        ("subnets", "Microsoft.Network/virtualNetworks/subnets"),
        ("virtualNetworkPeerings", "Microsoft.Network/virtualNetworks/virtualNetworkPeerings"),
    ],
}

# Top-level keys kept from a raw ARM / Resource Graph resource, in output order.
_RESOURCE_KEYS = ("id", "name", "type", "kind", "location", "zones", "sku", "plan", "managedBy",
                  "identity", "extendedLocation", "tags", "properties")

_SUPPORTED_VERSIONS_RE = re.compile(r"supported api-versions are '([^']+)'", re.I)


class CollectorOptions:
    """Filters and switches for a collection run."""

    def __init__(self, engine="auto", resource_group=None, rgtag_key=None, rgtag_value=None,
                 rtag_key=None, rtag_value=None, include_children=True, include_advisor=True,
                 workers=8):
        self.engine = engine
        self.resource_group = resource_group
        self.rgtag_key = rgtag_key
        self.rgtag_value = rgtag_value
        self.rtag_key = rtag_key
        self.rtag_value = rtag_value
        self.include_children = include_children
        self.include_advisor = include_advisor
        self.workers = max(1, int(workers or 1))


class ProviderCatalog:
    """Resource provider metadata: canonical type names and API versions."""

    def __init__(self, arm):
        self._arm = arm
        self._types = None  # lower type -> (canonical type, [api versions], default api version)

    def load(self, subscription_id):
        if self._types is not None:
            return
        types = {}
        try:
            for provider in self._arm.list(f"/subscriptions/{subscription_id}/providers", API_RESOURCES):
                namespace = provider.get("namespace") or ""
                for resource_type in provider.get("resourceTypes") or []:
                    canonical = f"{namespace}/{resource_type.get('resourceType', '')}"
                    types[canonical.lower()] = (
                        canonical,
                        resource_type.get("apiVersions") or [],
                        resource_type.get("defaultApiVersion"),
                    )
        except ArmError as exc:
            logger.warning("Could not load resource provider metadata: %s", exc)
        self._types = types

    def canonical_type(self, resource_type):
        """Return the type in ARM's canonical casing (Resource Graph lower-cases it)."""
        entry = (self._types or {}).get((resource_type or "").lower())
        return entry[0] if entry else resource_type

    def api_versions(self, resource_type):
        """API versions worth trying for a type, best first."""
        entry = (self._types or {}).get((resource_type or "").lower())
        if not entry:
            return []
        _, versions, default = entry
        stable = sorted((v for v in versions if not _is_preview(v)), reverse=True)
        preview = sorted((v for v in versions if _is_preview(v)), reverse=True)
        candidates = [default] + stable[:1] + preview[:1]
        return list(dict.fromkeys(v for v in candidates if v))


def _is_preview(api_version):
    return any(marker in api_version.lower() for marker in ("preview", "beta", "alpha", "rc", "privatepreview"))


def list_subscriptions(arm):
    """All subscriptions the credential can see."""
    return [
        {
            "subscriptionId": sub.get("subscriptionId"),
            "displayName": sub.get("displayName") or sub.get("subscriptionId"),
            "state": sub.get("state"),
            "tenantId": sub.get("tenantId"),
        }
        for sub in arm.list("/subscriptions", API_SUBSCRIPTIONS)
    ]


def resource_group_of(resource_id):
    """Resource group name embedded in a resource id ('' when there is none)."""
    parts = (resource_id or "").split("/")
    for index in range(len(parts) - 1):
        if parts[index].lower() == "resourcegroups":
            return parts[index + 1]
    return ""


def normalize_resource(raw, catalog=None):
    """Bring an ARM or Resource Graph resource into one common, lean shape."""
    resource = {}
    for key in _RESOURCE_KEYS:
        value = raw.get(key)
        if value in (None, "", {}, []):
            continue
        resource[key] = value
    if catalog is not None and resource.get("type"):
        resource["type"] = catalog.canonical_type(resource["type"])
    return resource


def _attach_to_known(recommendations, known_ids):
    """Move recommendations for resources we do not hold (deeper child
    resources) to the closest parent that is part of the inventory."""
    attached = {}
    for target, items in recommendations.items():
        current = target
        while current and current not in known_ids:
            current = parent_resource_id(current)
        if current:
            attached.setdefault(current, []).extend(items)
    return attached


class Collector:
    """Builds the inventory document written to output.json."""

    def __init__(self, arm, options=None, progress=print):
        self.arm = arm
        self.options = options or CollectorOptions()
        self.progress = progress or (lambda *_: None)
        self.catalog = ProviderCatalog(arm)

    # -- entry point -------------------------------------------------------
    def collect(self, subscription_ids=None):
        start = time.time()
        data = {
            "Properties": {
                "ScriptVersion": SCRIPT_VERSION,
                "Datestamp": str(datetime.datetime.now()),
                "Duration": None,
                "Engine": self.options.engine,
            },
            "Subscriptions": {},
            "ResourceGroups": {},
            "Objects": {},
        }

        known = {}
        try:
            known = {sub["subscriptionId"]: sub for sub in list_subscriptions(self.arm)}
        except ArmError as exc:
            if not subscription_ids:
                raise
            logger.warning("Could not list subscriptions: %s", exc)
        targets = list(subscription_ids) if subscription_ids else list(known)
        if not targets:
            self.progress("No subscriptions found for this identity. Does it have the Reader role?")

        engines_used = set()
        for index, subscription_id in enumerate(targets, start=1):
            info = known.get(subscription_id) or {"subscriptionId": subscription_id, "displayName": subscription_id}
            self.progress(f"Subscription {index}/{len(targets)}: {info['displayName']} ({subscription_id})")
            data["Subscriptions"][subscription_id] = dict(info)
            data["ResourceGroups"][subscription_id] = {}
            data["Objects"][subscription_id] = {}
            try:
                engines_used.add(self._collect_subscription(subscription_id, data))
            except ArmError as exc:
                logger.error("Subscription %s failed: %s", subscription_id, exc)
                self.progress(f"  ERROR: {exc}")
                data["Subscriptions"][subscription_id]["Error"] = str(exc)

        data["Properties"]["Engine"] = "+".join(sorted(e for e in engines_used if e)) or self.options.engine
        data["Properties"]["Duration"] = time.time() - start
        return data

    # -- one subscription --------------------------------------------------
    def _collect_subscription(self, subscription_id, data):
        options = self.options
        self.catalog.load(subscription_id)

        groups = self._resource_groups(subscription_id)
        rg_meta = data["ResourceGroups"][subscription_id]
        objects = data["Objects"][subscription_id]
        for group in groups:
            rg_meta[group["name"]] = {
                "id": group.get("id"),
                "location": group.get("location"),
                "tags": group.get("tags") or {},
            }
            objects[group["name"]] = []
        rg_by_lower = {name.lower(): name for name in rg_meta}
        filtered = bool(options.resource_group or (options.rgtag_key and options.rgtag_value))

        resources, engine = self._resources(subscription_id)
        if options.rtag_key and options.rtag_value:
            resources = [r for r in resources if (r.get("tags") or {}).get(options.rtag_key) == options.rtag_value]

        kept = []
        for resource in resources:
            rg_name = self._assign_group(resource, rg_by_lower, rg_meta, objects, filtered)
            if rg_name is not None:
                kept.append((rg_name, resource))

        children = self._children(kept) if options.include_children else []
        recommendations, unattached = ({}, [])
        if options.include_advisor:
            recommendations, unattached = self._advisor(subscription_id)
        if unattached:
            data["Subscriptions"][subscription_id]["Recommendations"] = unattached
        known_ids = {(resource.get("id") or "").lower() for _, resource in kept + children}
        recommendations = _attach_to_known(recommendations, known_ids)

        for rg_name, resource in kept + children:
            objects[rg_name].append({
                "ResourceType": resource.get("type", ""),
                "Details": resource,
                "Recommendations": recommendations.get((resource.get("id") or "").lower(), []),
            })
        for entries in objects.values():
            entries.sort(key=lambda e: (e["ResourceType"].lower(), (e["Details"].get("name") or "").lower()))

        attached = sum(len(entry["Recommendations"]) for entries in objects.values() for entry in entries)
        self.progress(
            f"  {len(objects)} resource groups, {len(kept)} resources via {engine}"
            + (f", {len(children)} child resources" if options.include_children else "")
            + (f", {attached + len(unattached)} Advisor recommendations" if options.include_advisor else "")
        )
        return engine

    def _resource_groups(self, subscription_id):
        options = self.options
        groups = list(self.arm.list(f"/subscriptions/{subscription_id}/resourcegroups", API_RESOURCES))
        if options.resource_group:
            wanted = options.resource_group.lower()
            groups = [g for g in groups if (g.get("name") or "").lower() == wanted]
            if not groups:
                self.progress(f"  Resource group '{options.resource_group}' not found in this subscription")
        if options.rgtag_key and options.rgtag_value:
            groups = [g for g in groups if (g.get("tags") or {}).get(options.rgtag_key) == options.rgtag_value]
        return sorted(groups, key=lambda g: (g.get("name") or "").lower())

    @staticmethod
    def _assign_group(resource, rg_by_lower, rg_meta, objects, filtered):
        """Resource group a resource is reported under, or None to drop it."""
        parsed = resource_group_of(resource.get("id"))
        name = rg_by_lower.get(parsed.lower())
        if name:
            return name
        if filtered:
            return None  # belongs to a resource group that was filtered out
        name = parsed or NO_RESOURCE_GROUP
        rg_by_lower[name.lower()] = name
        rg_meta[name] = {"id": None, "location": None, "tags": {}}
        objects[name] = []
        return name

    # -- resources ---------------------------------------------------------
    def _resources(self, subscription_id):
        engine = self.options.engine
        if engine in ("auto", "graph"):
            try:
                resources = self._resources_from_graph(subscription_id)
            except ArmError as exc:
                if engine == "graph":
                    raise
                logger.warning("Resource Graph unavailable (%s); falling back to ARM", exc)
                self.progress("  Resource Graph unavailable, falling back to ARM (slower)")
            else:
                if engine == "auto":
                    resources += self._missing_from_graph(subscription_id, resources)
                return resources, "Resource Graph"
        return self._resources_from_arm(subscription_id), "ARM"

    def _resources_from_graph(self, subscription_id):
        query = "resources"
        if self.options.resource_group:
            escaped = self.options.resource_group.replace("\\", "\\\\").replace("'", "\\'")
            query += f" | where resourceGroup =~ '{escaped}'"
        query += " | order by id asc"

        rows, skip_token, page_size = [], None, GRAPH_PAGE_SIZE
        while True:
            request_options = {"resultFormat": "objectArray", "$top": page_size}
            if skip_token:
                request_options["$skipToken"] = skip_token
            body = {"subscriptions": [subscription_id], "query": query, "options": request_options}
            try:
                page = self.arm.post("/providers/Microsoft.ResourceGraph/resources", API_RESOURCE_GRAPH, body)
            except ArmError as exc:
                if "ResponsePayloadTooLarge" in f"{exc.code} {exc.message}" and page_size > 10:
                    page_size //= 2  # very large resources: ask for smaller pages
                    continue
                raise
            rows.extend(page.get("data") or [])
            skip_token = page.get("$skipToken")
            if not skip_token:
                break
        return [normalize_resource(row, self.catalog) for row in rows]

    def _arm_listing(self, subscription_id):
        path = f"/subscriptions/{subscription_id}/resources"
        if self.options.resource_group:
            path = f"/subscriptions/{subscription_id}/resourceGroups/{self.options.resource_group}/resources"
        return list(self.arm.list(path, API_RESOURCES))

    def _missing_from_graph(self, subscription_id, graph_resources):
        """Resources ARM lists that Resource Graph did not return."""
        try:
            listing = self._arm_listing(subscription_id)
        except ArmError as exc:
            logger.warning("ARM completeness check skipped: %s", exc)
            return []
        seen = {(r.get("id") or "").lower() for r in graph_resources}
        missing = [item for item in listing if (item.get("id") or "").lower() not in seen]
        if missing:
            logger.info("%d resources not in Resource Graph, reading them from ARM", len(missing))
        return self._read_all(missing)

    def _resources_from_arm(self, subscription_id):
        return self._read_all(self._arm_listing(subscription_id))

    def _read_all(self, listing):
        if not listing:
            return []
        with ThreadPoolExecutor(max_workers=self.options.workers) as pool:
            return list(pool.map(self._read_resource, listing))

    def _read_resource(self, item):
        """GET one resource with full properties; fall back to the listing entry."""
        resource_id, resource_type = item.get("id"), item.get("type")
        tried, candidates, last_error = set(), self.catalog.api_versions(resource_type), None
        while candidates:
            api_version = candidates.pop(0)
            if api_version in tried:
                continue
            tried.add(api_version)
            try:
                full = self.arm.get(resource_id, api_version)
                if isinstance(full, dict) and full.get("id"):
                    # anything the GET leaves out is taken from the listing entry
                    return normalize_resource({**item, **full}, self.catalog)
                last_error = "unexpected response"
            except ArmError as exc:
                last_error = exc
                hinted = _SUPPORTED_VERSIONS_RE.search(exc.message)
                if hinted:  # ARM tells us which versions it would have accepted
                    versions = [v.strip() for v in hinted.group(1).split(",") if v.strip()]
                    stable = [v for v in versions if not _is_preview(v)] or versions
                    candidates.append(sorted(stable, reverse=True)[0])
                elif exc.status_code in (401, 403, 404):
                    break
        logger.warning("Only basic details for %s (%s)", resource_id, last_error or "no API version known")
        return normalize_resource(item, self.catalog)

    # -- children ----------------------------------------------------------
    def _children(self, kept):
        children, jobs = [], []
        for rg_name, resource in kept:
            type_lower = (resource.get("type") or "").lower()
            for key, child_type in EMBEDDED_CHILDREN.get(type_lower, []):
                for raw in (resource.get("properties") or {}).get(key) or []:
                    if isinstance(raw, dict) and raw.get("id"):
                        child = normalize_resource({**raw, "type": raw.get("type") or child_type}, self.catalog)
                        children.append((rg_name, child))
            for path, child_type, fallback_version, predicate in CHILD_COLLECTIONS.get(type_lower, []):
                if predicate is None or predicate(resource):
                    jobs.append((rg_name, resource, path, child_type, fallback_version))
        if jobs:
            with ThreadPoolExecutor(max_workers=self.options.workers) as pool:
                for rg_name, items in pool.map(self._list_children, jobs):
                    children.extend((rg_name, item) for item in items)
        return children

    def _list_children(self, job):
        rg_name, resource, path, child_type, fallback_version = job
        versions = self.catalog.api_versions(child_type)[:1] + [fallback_version]
        for api_version in dict.fromkeys(versions):
            try:
                raw_items = list(self.arm.list(f"{resource['id']}/{path}", api_version))
            except ArmError as exc:
                logger.debug("No %s for %s: %s", path, resource.get("name"), exc)
                continue
            items = []
            for raw in raw_items:
                if isinstance(raw, dict) and raw.get("id"):
                    items.append(normalize_resource({**raw, "type": raw.get("type") or child_type}, self.catalog))
            return rg_name, items
        return rg_name, []

    # -- advisor -----------------------------------------------------------
    def _advisor(self, subscription_id):
        """Advisor recommendations keyed by lower-case resource id."""
        by_resource, unattached = {}, []
        try:
            path = f"/subscriptions/{subscription_id}/providers/Microsoft.Advisor/recommendations"
            for recommendation in self.arm.list(path, API_ADVISOR):
                properties = recommendation.get("properties") or {}
                target = ((properties.get("resourceMetadata") or {}).get("resourceId") or "").lower()
                if not target:
                    marker = "/providers/microsoft.advisor/recommendations/"
                    target = (recommendation.get("id") or "").lower().split(marker)[0]
                if resource_group_of(target):
                    by_resource.setdefault(target, []).append(recommendation)
                else:
                    unattached.append(recommendation)
        except ArmError as exc:
            logger.warning("Advisor recommendations unavailable: %s", exc)
        return by_resource, unattached
