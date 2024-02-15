from azure.mgmt.streamanalytics import StreamAnalyticsManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_stream_analytics_job(resource, rg, stream_analytics_client, root_element, resource_node_ids):
    # Get the Stream Analytics Job
    stream_analytics_job = stream_analytics_client.streaming_jobs.get(rg.name, resource.name)
    
    print(f"Added Stream Analytics Job {stream_analytics_job.name}")
    stream_analytics_job_id = f"{stream_analytics_job.name}_{uuid.uuid4()}"
    resource_node_ids[stream_analytics_job_id] = stream_analytics_job_id  # Use the Stream Analytics Job name as the key
    stream_analytics_job_node = SubElement(root_element, 'mxCell', {'id': stream_analytics_job_id, 'value': stream_analytics_job.name, 'vertex': '1', 'parent': '1'})
    stream_analytics_job_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids
