from azure.mgmt.sql import SqlManagementClient

def handle_sql_db(resource, rg, sql_client):
    try:
        # Get the SQL database
        sql_database = sql_client.databases.get(rg.name, resource.name)
        print("Getting SQL Database...")

        # Add the details to the sql database dictionary
        sql_database_dict = sql_database.as_dict()

        return sql_database_dict

    except Exception as e:
        return {'Error': str(e)}