from azure.mgmt.sql import SqlManagementClient

def handle_sql_server(resource, rg, sql_client):
    try:
        print("Getting SQL Server...")
        # Get the sql_server
        server = sql_client.servers.get(rg.name, resource.name)

        # Add the keys to the app service plan dictionary
        server_dict = server.as_dict()

        return server_dict

    except Exception as e:
        return {'Error': str(e)}