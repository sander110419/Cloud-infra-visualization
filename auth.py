from azure.identity import ClientSecretCredential

def authenticate(tenant_id, client_id, client_secret):
    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    return credential
