from azure.mgmt.sql import SqlManagementClient

def handle_virtual_cluster(resource, rg, sql_client):
    try:
        print("Getting Virtual Cluster...")
        virtual_cluster = sql_client.virtual_clusters.get(rg.name, resource.name)
        virtual_cluster_dict = virtual_cluster.as_dict()

        return virtual_cluster_dict

    except Exception as e:
        return {'Error': str(e)}