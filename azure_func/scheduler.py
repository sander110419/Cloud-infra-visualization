from azure.mgmt.scheduler import SchedulerManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_scheduler_job_collection(resource, rg, scheduler_client, root_element, resource_node_ids):
    job_collection = scheduler_client.job_collections.get(rg.name, resource.name)
    print(f"Added Scheduler Job Collection {job_collection.name}")
    job_collection_id = f"{job_collection.name}_{uuid.uuid4()}"
    resource_node_ids[job_collection.name] = job_collection_id
    job_collection_node = SubElement(root_element, 'mxCell', {'id': job_collection_id, 'value': job_collection.name, 'vertex': '1', 'parent': '1'})
    job_collection_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
