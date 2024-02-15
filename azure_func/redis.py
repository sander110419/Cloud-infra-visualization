from azure.mgmt.redis import RedisManagementClient
from lxml.etree import Element, SubElement, tostring
import uuid

def handle_redis_cache(resource, rg, redis_client, root_element, resource_node_ids):
    # Get the Redis Cache
    redis_cache = redis_client.redis.get(rg.name, resource.name)
    
    print(f"Added Redis Cache {redis_cache.name}")
    redis_cache_id = f"{redis_cache.name}_{uuid.uuid4()}"
    resource_node_ids[redis_cache_id] = redis_cache_id  # Use the Redis Cache name as the key
    redis_cache_node = SubElement(root_element, 'mxCell', {'id': redis_cache_id, 'value': redis_cache.name, 'vertex': '1', 'parent': '1'})
    redis_cache_node.append(Element('mxGeometry', {'width': '80', 'height': '30', 'as': 'geometry'}))
    return root_element, resource_node_ids