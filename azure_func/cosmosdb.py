from azure.mgmt.cosmosdb import CosmosDBManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid


def handle_cosmosdb_account(resource, rg, cosmosdb_client, root_element, resource_node_ids):
    cosmosdb_account = cosmosdb_client.database_accounts.get(rg.name, resource.name)
    print(f"Added Cosmos DB Account {cosmosdb_account.name}")
    cosmosdb_account_id = f"{cosmosdb_account.name}_{uuid.uuid4()}"
    resource_node_ids[cosmosdb_account.name] = cosmosdb_account_id
    cosmosdb_account_node = SubElement(root_element, 'mxCell', {'id': cosmosdb_account_id, 'value': cosmosdb_account.name, 'vertex': '1', 'parent': '1'})
    cosmosdb_account_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
