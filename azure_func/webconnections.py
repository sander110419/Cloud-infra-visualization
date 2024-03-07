from azure.mgmt.web import WebSiteManagementClient

def handle_web_connections(resource, rg, web_client):
    try:
        print("Getting Web Connection...")
        connection = web_client.web_apps.list_connection_strings(rg.name, resource.name)
        connection_dict = {conn_str.name: conn_str.connection_string for conn_str in connection.value}

        return connection_dict

    except Exception as e:
        return {'Error': str(e)}