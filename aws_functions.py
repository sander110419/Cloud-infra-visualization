import argparse
import datetime
import time
import json
import logging
import boto3

def authenticate(access_key_id, secret_access_key):
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )
    return session

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, 'as_dict'):
            return obj.as_dict()
        return super().default(obj)
    
def parse_arguments():
    parser = argparse.ArgumentParser(description='AWS authentication parameters')
    parser.add_argument('--log_level', type=str, required=False, default='INFO', help='Log Level')
    parser.add_argument('--access_key_id', type=str, required=True, help='Access Key ID')
    parser.add_argument('--secret_access_key', type=str, required=True, help='Secret Access Key')
    parser.add_argument('--region_name', type=str, required=False, help='Region Name')

    #output args
    parser.add_argument('--output_xlsx', action='store_true', help='Output to Excel')
    parser.add_argument('--output_folder', type=str, required=False, help='Output Folder')

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

def get_regions(session, region_name):
    if region_name:
        regions = [region_name]
    else:
        regions = session.get_available_regions('ec2')

    return regions