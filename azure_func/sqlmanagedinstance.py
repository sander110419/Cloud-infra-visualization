from azure.mgmt.sql import SqlManagementClient

def handle_sql_managed_instances(resource, rg, sql_client):
    try:
        print("Getting SQL Managed Instance...")
        sql_managed_instance = sql_client.managed_instances.get(rg.name, resource.name)
        sql_managed_instance_dict = sql_managed_instance.as_dict()

        return sql_managed_instance_dict

    except Exception as e:
        return {'Error': str(e)}