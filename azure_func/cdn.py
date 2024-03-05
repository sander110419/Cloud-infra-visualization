from azure.mgmt.cdn import CdnManagementClient

def handle_cdn_profile(resource, rg, cdn_client):
    try:
        # Get the CDN profile
       cdn_profile = cdn_client.profiles.get(rg.name, resource.name)
       print("Getting CDN profile...")

        # Add the keys to the storage account dictionary
       cdn_profile_dict = cdn_profile.as_dict()

       return cdn_profile_dict

    except Exception as e:
        return {'Error': str(e)}