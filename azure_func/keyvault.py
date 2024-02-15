from azure.mgmt.keyvault import KeyVaultManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_key_vault(resource, rg, kv_client, root_element, resource_node_ids):
    # Get the key vault
    key_vault = kv_client.vaults.get(rg.name, resource.name)
    
    print(f"Added Key Vault {key_vault.name}")
    key_vault_id = f"{key_vault.name}_{uuid.uuid4()}"
    resource_node_ids[key_vault_id] = key_vault_id  # Use the key vault name as the key
    key_vault_node = SubElement(root_element, 'mxCell', {'id': key_vault_id, 'value': key_vault.name, 'vertex': '1', 'parent': '1'})
    key_vault_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids