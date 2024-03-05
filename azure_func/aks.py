from azure.mgmt.containerservice import ContainerServiceClient

def handle_aks_service(resource, rg, aks_client, root_element, resource_node_ids):
    try:
        # Get the AKS
        aks_service = aks_client.managed_clusters.get(rg.name, resource.name)
        print("Getting Azure Kubernetes Cluster...")

        # Add the keys to the storage account dictionary
        aks_service_dict = aks_service.as_dict()

        return aks_service_dict

    except Exception as e:
        return {'Error': str(e)}