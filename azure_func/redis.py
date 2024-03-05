from azure.mgmt.redis import RedisManagementClient

def handle_redis_cache(resource, rg, redis_client):
    try:
        # Get the Redis Cache
        redis_cache = redis_client.redis.get(rg.name, resource.name)
        print("Getting Redis Cache...")

        # Add the keys to the storage account dictionary
        redis_cache_dict = redis_cache.as_dict()

        return redis_cache_dict

    except Exception as e:
        return {'Error': str(e)}