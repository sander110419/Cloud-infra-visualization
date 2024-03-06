from azure.mgmt.sql import SqlManagementClient

def handle_sql_db(resource, rg, sql_client):
    try:
        # Split the resource id to get the server name
        resource_id_parts = resource.id.split('/')
        server_name = resource_id_parts[resource_id_parts.index('servers') + 1]

        # Get all SQL databases for the given server
        sql_databases = sql_client.databases.list_by_server(rg.name, server_name)
        print("Getting SQL Databases...")

        # Add the details to the sql database dictionary
        sql_databases_dict = [db.as_dict() for db in sql_databases]

        return sql_databases_dict

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'Error': str(e)} 