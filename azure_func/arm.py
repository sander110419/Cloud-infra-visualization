"""Minimal Azure Resource Manager (ARM) REST client.

The whole tool talks to Azure through this one class. Using the REST API
directly (instead of one SDK package per Azure service) is what makes it
possible to cover *every* resource type: anything ARM knows about can be
listed and read with the same handful of calls.
"""
import logging
from urllib.parse import quote

from azure.core import PipelineClient
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest

DEFAULT_ENDPOINT = "https://management.azure.com"
USER_AGENT = "cloud-infra-visualization"

# API versions of the few "platform" endpoints we call directly. API versions
# of individual resource types are discovered at runtime (see ProviderCatalog).
API_SUBSCRIPTIONS = "2022-12-01"
API_RESOURCES = "2021-04-01"
API_RESOURCE_GRAPH = "2022-10-01"
API_ADVISOR = "2023-01-01"

# Characters that may appear unescaped in an ARM path.
_SAFE_PATH_CHARS = "/()@:$,;=+*'!~-._"

logger = logging.getLogger(__name__)


class ArmError(Exception):
    """An ARM call returned an HTTP error."""

    def __init__(self, status_code, code, message, url=""):
        super().__init__(f"{status_code} {code}: {message}")
        self.status_code = status_code
        self.code = code or ""
        self.message = message or ""
        self.url = url


class ArmClient:
    """Authenticated, retrying JSON client for the ARM REST API."""

    def __init__(self, credential, endpoint=DEFAULT_ENDPOINT):
        self.endpoint = (endpoint or DEFAULT_ENDPOINT).rstrip("/")
        # Plain http is only ever used against a local test double.
        self._insecure = self.endpoint.lower().startswith("http://")
        self._client = PipelineClient(
            base_url=self.endpoint,
            policies=[
                policies.RequestIdPolicy(),
                policies.HeadersPolicy({"Accept": "application/json"}),
                policies.UserAgentPolicy(USER_AGENT),
                policies.ContentDecodePolicy(),
                policies.RedirectPolicy(),
                # Retries 408/429/5xx and honours Retry-After, which is what
                # ARM and Resource Graph use for throttling.
                policies.RetryPolicy(retry_total=8, retry_backoff_factor=1.0, retry_backoff_max=90),
                policies.BearerTokenCredentialPolicy(credential, f"{self.endpoint}/.default"),
            ],
        )

    def close(self):
        self._client.close()

    # -- low level ---------------------------------------------------------
    def _url(self, path):
        if path.lower().startswith(("http://", "https://")):
            return path  # absolute URL, e.g. a nextLink
        if not path.startswith("/"):
            path = "/" + path
        return self.endpoint + quote(path, safe=_SAFE_PATH_CHARS)

    def _send(self, method, path, api_version=None, params=None, body=None):
        url = self._url(path)
        query = dict(params or {})
        if api_version and "api-version=" not in url:
            query["api-version"] = api_version
        request = HttpRequest(method, url, params=query or None, json=body)
        kwargs = {"enforce_https": False} if self._insecure else {}
        response = self._client.send_request(request, **kwargs)
        if response.status_code >= 400:
            code, message = _parse_error(response)
            raise ArmError(response.status_code, code, message, url)
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise ArmError(response.status_code, "InvalidJson", str(exc), url) from exc

    # -- public ------------------------------------------------------------
    def get(self, path, api_version=None, params=None):
        """GET a single ARM document."""
        return self._send("GET", path, api_version, params)

    def post(self, path, api_version, body, params=None):
        """POST a JSON body and return the JSON response."""
        return self._send("POST", path, api_version, params, body)

    def list(self, path, api_version=None, params=None):
        """GET a collection, following ``nextLink`` paging. Yields items."""
        page = self._send("GET", path, api_version, params)
        while True:
            if isinstance(page, list):  # a few old APIs return a bare array
                yield from page
                return
            yield from page.get("value") or []
            next_link = page.get("nextLink") or page.get("@odata.nextLink")
            if not next_link:
                return
            page = self._send("GET", next_link)


def _parse_error(response):
    """Extract (code, message) from an ARM error response."""
    try:
        payload = response.json()
    except Exception:  # noqa: BLE001 - body may be empty or not JSON
        return "", (response.text() or response.reason or "")[:500]
    error = payload.get("error", payload) if isinstance(payload, dict) else {}
    if not isinstance(error, dict):
        return "", str(error)[:500]
    message = error.get("message") or ""
    # Resource Graph nests the interesting part in "details".
    for detail in error.get("details") or []:
        if isinstance(detail, dict) and detail.get("message"):
            message = f"{message} {detail.get('code', '')}: {detail['message']}".strip()
            if not error.get("code") or error.get("code") == "BadRequest":
                error = {**error, "code": detail.get("code") or error.get("code")}
            break
    return error.get("code") or "", message[:1000]
