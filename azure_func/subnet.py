from azure.mgmt.network import NetworkManagementClient

def handle_all_subnets(rg, network_client):
    try:
        # Get all Virtual Networks in the Resource Group
        vnets = network_client.virtual_networks.list(rg.name)
        
        all_subnets = []
        
        # Iterate over each Virtual Network
        for vnet in vnets:
            # Get all Subnets in the current Virtual Network
            subnets = network_client.subnets.list(rg.name, vnet.name)
            
            # Iterate over each Subnet
            for subnet in subnets:
                # Add the keys to the subnet dictionary
                subnet_dict = subnet.as_dict()
                
                # Append the subnet dictionary to the list of all subnets
                all_subnets.append(subnet_dict)
        
        return all_subnets

    except Exception as e:
        return {'Error': str(e)}