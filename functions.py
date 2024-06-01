import argparse
import datetime
import time
import json
import logging
from azure_func import azure_imports
from azure.identity import ClientSecretCredential, CertificateCredential, InteractiveBrowserCredential

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super().default(obj)
    
def parse_arguments():
    parser = argparse.ArgumentParser(description='Azure authentication parameters')
    parser.add_argument('--log_level', type=str, required=False, default='INFO', help='Log Level')
    parser.add_argument('--tenant_id', type=str, required=True, help='Tenant ID')
    parser.add_argument('--client_id', type=str, required=True, help='Client ID')
    parser.add_argument('--client_secret', type=str, required=False, help='Client Secret')
    parser.add_argument('--certificate_path', type=str, required=False, help='Path to the certificate file')
    parser.add_argument('--use_device_code', action='store_true', help='Use device code authentication')
    parser.add_argument('--interactive_login', action='store_true', help='Use interactive login')
   
    #filter args
    parser.add_argument('--subscription_id', type=str, required=False, help='Subscription ID')
    parser.add_argument('--resource_group', type=str, required=False, help='Resource Group')
    parser.add_argument('--rgtag_key', type=str, required=False, help='Filter resource groups by this case-sensitive resource group Tag Key')
    parser.add_argument('--rgtag_value', type=str, required=False, help='Filter resource groups by this case-sensitive resource Group Tag Value')
    parser.add_argument('--rtag_key', type=str, required=False, help='Filter resources by this case-sensitive resource Tag Key')
    parser.add_argument('--rtag_value', type=str, required=False, help='Filter resources by this case-sensitive resource Tag Value')

    #output args
    parser.add_argument('--output_xlsx', action='store_true', help='Output to Excel')
    parser.add_argument('--output_folder', type=str, required=False, help='Output Folder')
    parser.add_argument('--output_drawio', action='store_true', help='Output to XML')


    return parser.parse_args()

def set_up_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(filename="CloudInfraViz.log", 
                        format='%(asctime)s %(message)s', 
                        filemode='w',
                        level=numeric_level)

def initialize_data():
    start_time = time.time()

    data = {
        'Properties': {
            'ScriptVersion': '0.1',
            'Datestamp': str(datetime.datetime.now()),
            'Duration': None  # Will be updated at the end of the script
        },
        'Objects': {}
    }

    return data, start_time

def authenticate_to_azure(tenant_id, client_id, client_secret=None, certificate_path=None, use_device_code=None, interactive_login=False):
    if interactive_login:
        credential = InteractiveBrowserCredential(client_id=client_id)
    elif use_device_code:
        # Use DeviceCodeCredential when use_device_code is True
        credential = azure_imports.DeviceCodeCredential(client_id=client_id, tenant_id=tenant_id)
    elif certificate_path:
        try:
            with open(certificate_path, "rb") as file:
                pem_data = file.read()
            logging.info(f"Successfully read the certificate file from: {certificate_path}")
        except Exception as e:
            logging.error(f"Error reading the certificate file from: {certificate_path}. Error: {str(e)}")
            raise e

        credential = CertificateCredential(tenant_id=tenant_id, client_id=client_id, certificate_data=pem_data)
    else:
        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

    subscription_client = azure_imports.SubscriptionClient(credential)

    return credential, subscription_client

def get_subscriptions(subscription_client, subscription_id):
    if subscription_id:
        subscriptions = [subscription_id]
    else:
        subscriptions = [sub.subscription_id for sub in subscription_client.subscriptions.list()]

    return subscriptions