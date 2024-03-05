from azure.mgmt.servicefabric import ServiceFabricManagementClient

def handle_service_fabric_cluster(resource, rg, sf_client):
    try:
        # Get the service_fabric
        sf_cluster = sf_client.clusters.get(rg.name, resource.name)
        print("Getting Service Fabric Cluster...")

        # Add the keys to the storage account dictionary
        sf_cluster_dict = sf_cluster.as_dict()

        return sf_cluster_dict

    except Exception as e:
        return {'Error': str(e)}