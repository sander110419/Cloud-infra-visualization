from azure.mgmt.network import NetworkManagementClient

def handle_application_gateway_waf_policies(resource, rg, network_client):
    try:
        # Get the Application Gateway WAF Policy
        waf_policy = network_client.application_gateway_waf_policies.get(rg.name, resource.name)
        print("Getting Application Gateway WAF Policy...")

        # Add the keys to the WAF policy dictionary
        waf_policy_dict = waf_policy.as_dict()

        return waf_policy_dict

    except Exception as e:
        return {'Error': str(e)}