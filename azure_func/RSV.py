from azure.mgmt.recoveryservices import RecoveryServicesClient

def handle_recovery_services_vault(resource, rg, recovery_services_client):
    try:
        # Get the recovery services vault
        recovery_services_vault = recovery_services_client.vaults.get(rg.name, resource.name)
        print("Getting Recovery Services Vault...")

        # Add the keys to the recovery services vault dictionary
        recovery_services_vault_dict = recovery_services_vault.as_dict()

        return recovery_services_vault_dict

    except Exception as e:
        return {'Error': str(e)}