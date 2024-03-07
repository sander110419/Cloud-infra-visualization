from azure.mgmt.compute import ComputeManagementClient

def handle_proximity_placement_group(resource, rg, compute_client):
    try:
        # Get the Proximity Placement Group
        proximity_placement_group = compute_client.proximity_placement_groups.get(rg.name, resource.name)
        print("Getting Proximity Placement Group...")

        # Add the keys to the Proximity Placement Group dictionary
        proximity_placement_group_dict = proximity_placement_group.as_dict()

        return proximity_placement_group_dict

    except Exception as e:
        return {'Error': str(e)}