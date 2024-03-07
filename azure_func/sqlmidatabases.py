from azure.mgmt.sql import SqlManagementClient

def handle_sql_managed_instances_db(resource, rg, sql_client):
    try:
        # Split the resource id to get the server name
        resource_id_parts = resource.id.split('/')
        server_name = resource_id_parts[resource_id_parts.index('managedInstances') + 1]

        # Get all SQL databases for the given server
        databases = sql_client.databases.list_by_instance(rg.name, server_name)
        print("Getting Databases in Managed Instance...")

        # Add the details to the sql database dictionary
        sql_databases_dict = [db.as_dict() for db in databases]

        return sql_databases_dict

    except Exception as e:
        return {'Error': str(e)}