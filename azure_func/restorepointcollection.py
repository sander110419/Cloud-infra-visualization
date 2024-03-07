from azure.mgmt.compute import ComputeManagementClient

def handle_restore_point_collections(resource, rg, compute_client):
    try:
        print("Getting Restore Point Collection...")
        restore_point_collection = compute_client.restore_point_collections.get(rg.name, resource.name)
        restore_point_collection_dict = restore_point_collection.as_dict()

        return restore_point_collection_dict

    except Exception as e:
        return {'Error': str(e)}