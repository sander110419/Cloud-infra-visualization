def list_ec2_instances(session, region):
    ec2 = session.client('ec2', region_name=region)
    instances = []
    for reservation in ec2.describe_instances()['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)
    return instances

def list_s3_buckets(session, region):
    s3 = session.client('s3', region_name=region)
    buckets = []
    for bucket in s3.list_buckets()['Buckets']:
        bucket_info = s3.get_bucket_acl(Bucket=bucket['Name'])
        buckets.append(bucket_info)
    return buckets

def list_dynamodb_tables(session, region):
    dynamodb = session.client('dynamodb', region_name=region)
    tables = []
    for table in dynamodb.list_tables()['TableNames']:
        table_info = dynamodb.describe_table(TableName=table)
        tables.append(table_info)
    return tables

def list_rds_instances(session, region):
    rds = session.client('rds', region_name=region)
    instances = []
    for instance in rds.describe_db_instances()['DBInstances']:
        instances.append(instance)
    return instances

def list_lambda_functions(session, region):
    lambda_client = session.client('lambda', region_name=region)
    functions = []
    for function in lambda_client.list_functions()['Functions']:
        functions.append(function)
    return functions

def list_iam_users(session, region):
    iam = session.client('iam', region_name=region)
    users = []
    for user in iam.list_users()['Users']:
        users.append(user)
    return users

def list_elastic_load_balancers(session, region):
    elb = session.client('elbv2', region_name=region)
    load_balancers = []
    for lb in elb.describe_load_balancers()['LoadBalancers']:
        load_balancers.append(lb)
    return load_balancers

def list_sns_topics(session, region):
    sns = session.client('sns', region_name=region)
    topics = []
    for topic in sns.list_topics()['Topics']:
        topics.append(topic)
    return topics

def list_sqs_queues(session, region):
    sqs = session.client('sqs', region_name=region)
    queues = []
    for queue in sqs.list_queues()['QueueUrls']:
        queues.append(queue)
    return queues

def list_cloudformation_stacks(session, region):
    cf = session.client('cloudformation', region_name=region)
    stacks = []
    for stack in cf.list_stacks()['StackSummaries']:
        stacks.append(stack)
    return stacks

