from azure.mgmt.sql import SqlManagementClient

def handle_sql_server(resource, rg, sql_client):
    try:
        print("Getting SQL Server...")
        # Get the sql_server
        server = sql_client.servers.get(rg.name, resource.name)

        # Add the keys to the app service plan dictionary
        server_dict = server.as_dict()

        print("Getting DBs...")
        # Get the databases running on the server
        dbs = sql_client.databases.list_by_server(rg.name, server.name)
        
        # Convert the databases to a list of dictionaries
        db_list = [db.as_dict() for db in dbs]

        # Add the databases to the server dictionary
        server_dict['DBs'] = db_list

        return server_dict

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'Error': str(e)}