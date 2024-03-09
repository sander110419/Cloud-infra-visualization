import argparse
import datetime
import time
import json
from azure_func import azure_imports
from azure.identity import ClientSecretCredential

def authenticate(tenant_id, client_id, client_secret):
    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    return credential

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super().default(obj)
    
def parse_arguments():
    parser = argparse.ArgumentParser(description='Azure authentication parameters')
    parser.add_argument('--tenant_id', type=str, required=True, help='Tenant ID')
    parser.add_argument('--client_id', type=str, required=True, help='Client ID')
    parser.add_argument('--client_secret', type=str, required=True, help='Client Secret')
    parser.add_argument('--subscription_id', type=str, required=False, help='Subscription ID')
    parser.add_argument('--output_xlsx', action='store_true', help='Output to Excel')
    parser.add_argument('--output_folder', type=str, required=False, help='Output Folder')

    return parser.parse_args()

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

def authenticate_to_azure(tenant_id, client_id, client_secret):
    credential = authenticate(tenant_id, client_id, client_secret)
    subscription_client = azure_imports.SubscriptionClient(credential)

    return credential, subscription_client

def get_subscriptions(subscription_client, subscription_id):
    if subscription_id:
        subscriptions = [subscription_id]
    else:
        subscriptions = [sub.subscription_id for sub in subscription_client.subscriptions.list()]

    return subscriptions