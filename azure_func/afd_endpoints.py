from azure.mgmt.cdn import CdnManagementClient

def handle_afd_endpoints(resource, rg, cdn_client):
    try:
        # Get the AFD Endpoint
        afd_endpoint = cdn_client.afdendpoints.get(rg.name, resource.name)
        print("Getting AFD Endpoint...")

        # Add the keys to the AFD endpoint dictionary
        afd_endpoint_dict = afd_endpoint.as_dict()

        return afd_endpoint_dict

    except Exception as e:
        return {'Error': str(e)}
