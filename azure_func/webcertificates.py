from azure.mgmt.web import WebSiteManagementClient

def handle_web_certificate(resource, rg, web_client):
    try:
        print("Getting Web Certificate...")
        # Get the web certificate
        certificate = web_client.certificates.get(rg.name, resource.name)

        # Add the keys to the web certificate dictionary
        certificate_dict = certificate.as_dict()

        return certificate_dict

    except Exception as e:
        return {'Error': str(e)}