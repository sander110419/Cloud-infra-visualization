import argparse
import logging
import os
import sys

from azure.identity import (
    AzureCliCredential,
    CertificateCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    InteractiveBrowserCredential,
)

from azure_func.arm import DEFAULT_ENDPOINT, ArmClient
from azure_func.collector import list_subscriptions

LOG_FILE = "CloudInfraViz.log"


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="Document and visualise an Azure environment: JSON, Excel, Word, draw.io and HTML output.")
    parser.add_argument('--log_level', type=str, default='INFO', help='Log level for CloudInfraViz.log (default INFO)')

    auth = parser.add_argument_group('authentication (values default to the AZURE_* environment variables)')
    auth.add_argument('--tenant_id', type=str, default=os.environ.get('AZURE_TENANT_ID'), help='Tenant ID')
    auth.add_argument('--client_id', type=str, default=os.environ.get('AZURE_CLIENT_ID'), help='Client (application) ID')
    auth.add_argument('--client_secret', type=str, default=os.environ.get('AZURE_CLIENT_SECRET'),
                      help='Client secret. Prefer the AZURE_CLIENT_SECRET environment variable: '
                           'command line arguments end up in your shell history')
    auth.add_argument('--certificate_path', type=str, default=os.environ.get('AZURE_CLIENT_CERTIFICATE_PATH'),
                      help='Path to a PEM/PFX certificate for the client ID')
    auth.add_argument('--use_device_code', action='store_true', help='Use device code authentication')
    auth.add_argument('--interactive_login', action='store_true', help='Interactive browser login to the client ID')
    auth.add_argument('--user_login', action='store_true', help='Interactive browser login with your own account')
    auth.add_argument('--use_cli', action='store_true', help='Use the account logged in to the Azure CLI (az login)')

    scope = parser.add_argument_group('scope')
    scope.add_argument('--subscription_id', action='append', default=None,
                       help='Subscription ID. Repeat or separate with commas for several; default is all')
    scope.add_argument('--resource_group', type=str, help='Only this resource group')
    scope.add_argument('--rgtag_key', type=str, help='Filter resource groups by this case-sensitive tag key')
    scope.add_argument('--rgtag_value', type=str, help='Filter resource groups by this case-sensitive tag value')
    scope.add_argument('--rtag_key', type=str, help='Filter resources by this case-sensitive tag key')
    scope.add_argument('--rtag_value', type=str, help='Filter resources by this case-sensitive tag value')

    collection = parser.add_argument_group('collection')
    collection.add_argument('--engine', choices=['auto', 'graph', 'arm'], default='auto',
                            help='auto: Azure Resource Graph, completed and backed up by ARM (default). '
                                 'graph: Resource Graph only. arm: ARM only (slower)')
    collection.add_argument('--skip_children', action='store_true',
                            help='Do not collect child resources such as queues, blob containers and subnets')
    collection.add_argument('--skip_advisor', action='store_true', help='Do not collect Azure Advisor recommendations')
    collection.add_argument('--workers', type=int, default=8, help='Parallel requests to Azure (default 8)')
    collection.add_argument('--arm_endpoint', type=str, default=os.environ.get('AZURE_ARM_ENDPOINT', DEFAULT_ENDPOINT),
                            help='Resource Manager endpoint, for sovereign clouds '
                                 '(e.g. https://management.usgovcloudapi.net)')
    collection.add_argument('--input_json', type=str,
                            help='Skip Azure and build the outputs from an existing output.json')

    output = parser.add_argument_group('output')
    output.add_argument('--output_folder', type=str, help='Output folder (default ./output)')
    output.add_argument('--output_xlsx', action='store_true', help='Output to Excel')
    output.add_argument('--output_docx', action='store_true', help='Output to Docx')
    output.add_argument('--output_drawio', action='store_true', help='Output a draw.io diagram')
    output.add_argument('--output_html', '--output_mermaid', dest='output_html', action='store_true',
                        help='Output a mermaid.js flowchart as HTML')
    output.add_argument('--drawio_icons', choices=['embedded', 'library'], default='embedded',
                        help='embedded: icons are stored in the .drawio file, works everywhere (default). '
                             "library: reference the Azure icons that ship with draw.io, for files less "
                             "than half the size")

    args = parser.parse_args(argv)
    args.subscription_ids = [part.strip() for value in (args.subscription_id or [])
                             for part in value.split(',') if part.strip()]
    return args


def set_up_logging(log_level):
    numeric_level = getattr(logging, str(log_level).upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(filename=LOG_FILE,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s',
                        filemode='w',
                        level=numeric_level,
                        force=True)
    # Problems should also be visible to whoever is running the tool.
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(console)
    # The Azure SDK is chatty about every token request.
    logging.getLogger('azure').setLevel(max(numeric_level, logging.WARNING))


def build_credential(tenant_id=None, client_id=None, client_secret=None, certificate_path=None,
                     use_device_code=False, interactive_login=False, user_login=False, use_cli=False):
    """Create the azure-identity credential for the chosen way of logging in."""
    if interactive_login:
        return InteractiveBrowserCredential(**_only_set(client_id=client_id, tenant_id=tenant_id))
    if use_device_code:
        return DeviceCodeCredential(**_only_set(client_id=client_id, tenant_id=tenant_id))
    if user_login:
        return InteractiveBrowserCredential(**_only_set(tenant_id=tenant_id))
    if use_cli:
        return AzureCliCredential(**_only_set(tenant_id=tenant_id))
    if not (tenant_id and client_id):
        raise ValueError('No way to log in. Give --tenant_id and --client_id with a secret or certificate '
                         '(or set AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET), or use '
                         '--user_login, --use_cli, --use_device_code or --interactive_login.')
    if certificate_path:
        return CertificateCredential(tenant_id=tenant_id, client_id=client_id, certificate_path=certificate_path)
    if client_secret:
        return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    raise ValueError('A client ID needs --client_secret (or AZURE_CLIENT_SECRET) or --certificate_path.')


def _only_set(**values):
    return {key: value for key, value in values.items() if value}


def authenticate_to_azure(tenant_id, client_id, client_secret=None, certificate_path=None, use_device_code=None,
                          interactive_login=False, user_login=False, use_cli=False, arm_endpoint=DEFAULT_ENDPOINT):
    """Return ``(credential, arm_client)`` for the given login details."""
    credential = build_credential(tenant_id, client_id, client_secret, certificate_path, use_device_code,
                                  interactive_login, user_login, use_cli)
    return credential, ArmClient(credential, arm_endpoint)


def get_subscriptions(arm_client, subscription_id=None):
    """``[(subscription id, display name)]`` visible to the identity (or just the requested one)."""
    subscriptions = [(sub['subscriptionId'], sub['displayName']) for sub in list_subscriptions(arm_client)]
    if subscription_id:
        subscriptions = [sub for sub in subscriptions if sub[0] == subscription_id] or [(subscription_id, subscription_id)]
    return subscriptions
