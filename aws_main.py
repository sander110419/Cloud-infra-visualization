import boto3
from aws_func.service_functions import *

def list_regions():
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

def list_all_resources(access_key, secret_key):
    # Specify a default region, such as 'us-west-1'
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-west-1'  # replace with your preferred region
    )
    
    ec2 = session.client('ec2')
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    resource_list = {}

    for region in regions:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region  # use the current region
        )
        resource_list[region] = {
        'EC2': list_ec2_instances(session, region),
        'S3': list_s3_buckets(session, region),
        'DynamoDB': list_dynamodb_tables(session, region),
        'RDS': list_rds_instances(session, region),
        'Lambda': list_lambda_functions(session, region),
        'IAM': list_iam_users(session, region),
            # add other services here...
        }

    return resource_list


def validate_credentials(access_key, secret_key):
    try:
        client = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        response = client.get_caller_identity()
        return True
    except Exception as e:
        print(f"Invalid credentials: {e}")
        return False

def main():
    access_key = ''
    secret_key = ''

    if validate_credentials(access_key, secret_key):
        print("Credentials are valid.")
    else:
        print("Credentials are invalid.")
        return  # Exit the function if credentials are invalid

    resources = list_all_resources(access_key, secret_key)

    for region, services in resources.items():
        print(f"Region: {region}")
        for service, resource_ids in services.items():
            print(f"{service}: {resource_ids}")

if __name__ == "__main__":
    main()