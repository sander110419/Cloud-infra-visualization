from azure.mgmt.network import NetworkManagementClient

def handle_route_tables(resource, rg, network_client):
    try:
        # Get the Route Table
        route_table = network_client.route_tables.get(rg.name, resource.name)
        print("Getting Route Table...")

        # Add the keys to the Route Table dictionary
        route_table_dict = route_table.as_dict()

        return route_table_dict

    except Exception as e:
        return {'Error': str(e)}