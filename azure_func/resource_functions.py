def handle_resource(get_resource_func, rg, resource):
    """
    Handles Azure resources by getting the resource and converting it to a dictionary.
    
    Parameters:
    get_resource_func (function): A function that gets the desired resource.
    rg (ResourceGroup): The resource group containing the resource.
    resource (Resource): The resource to handle.

    Returns:
    dict: A dictionary representation of the resource, or an error message if an exception occurred.
    """
    try:
        # Get the resource
        resource_obj = get_resource_func(rg.name, resource.name)

        # Convert the resource to a dictionary
        resource_dict = resource_obj.as_dict()

        return resource_dict

    except Exception as e:
        return {'Error': str(e)}

def handle_container_registry(resource, rg, container_registry_client):
    return handle_resource(container_registry_client.registries.get, rg, resource)
    
def handle_action_rules(resource, rg, alertsmanagement_client):
    return handle_resource(alertsmanagement_client.action_rules.get_by_name, rg, resource)

def handle_frontdoor_cdn(resource, rg, cdn_client):
    return handle_resource(cdn_client.profiles.get, rg, resource)

def handle_aks_service(resource, rg, aks_client):
    return handle_resource(aks_client.managed_clusters.get, rg, resource)

def handle_api_management(resource, rg, apim_client):
    return handle_resource(apim_client.api_management_service.get, rg, resource)

def handle_application_gateway_waf_policies(resource, rg, network_client):
    return handle_resource(network_client.web_application_firewall_policies.get, rg, resource)

def handle_app_service_plan(resource, rg, web_client):
    return handle_resource(web_client.app_service_plans.get, rg, resource)

def handle_appservices(resource, rg, web_client):
    return handle_resource(web_client.web_apps.get, rg, resource)

def handle_batch_account(resource, rg, batch_client):
    return handle_resource(batch_client.batch_account.get, rg, resource)

def handle_bot_service(resource, rg, bot_service_client):
    return handle_resource(bot_service_client.bots.get, rg, resource)

def handle_cdn_profile(resource, rg, cdn_client):
    return handle_resource(cdn_client.profiles.get, rg, resource)

def handle_container_instance(resource, rg, container_instance_client):
    return handle_resource(container_instance_client.container_groups.get, rg, resource)

def handle_cognitive_service(resource, rg, cognitive_client):
    return handle_resource(cognitive_client.accounts.get, rg, resource)
    
def handle_communication_services(resource, rg, communication_client):
    return handle_resource(communication_client.communication_services.get, rg, resource)
    
def handle_container_app(resource, rg, containerapp_client):
    return handle_resource(containerapp_client.container_apps.get, rg, resource)
    
def handle_container_images(resource, rg, container_registry_client):
    return handle_resource(container_registry_client.container_images.get, rg, resource)
    
def handle_cosmosdb_account(resource, rg, cosmosdb_client):
    return handle_resource(cosmosdb_client.database_accounts.get, rg, resource)
    
def handle_data_factory(resource, rg, data_factory_client):
    return handle_resource(data_factory_client.factories.get, rg, resource)
    
def handle_data_lake_store(resource, rg, datalake_store_client):
    return handle_resource(datalake_store_client.account.get, rg, resource)
    
def handle_devtest_lab(resource, rg, devtest_client):
    return handle_resource(devtest_client.labs.get, rg, resource)
    
def handle_disk(resource, rg, compute_client):
    return handle_resource(compute_client.disks.get, rg, resource)
    
def handle_event_grids(resource, rg, event_grid_client):
    return handle_resource(event_grid_client.topics.get, rg, resource)
    
def handle_event_grid_subscriptions(resource, rg, event_grid_client):
    return handle_resource(event_grid_client.event_subscriptions.get, rg, resource)
    
def handle_event_hub_namespaces(resource, rg, eventhub_client):
    return handle_resource(eventhub_client.namespaces.get, rg, resource)
    
def handle_image_galleries(resource, rg, compute_client):
    return handle_resource(compute_client.galleries.get, rg, resource)
    
def handle_insights_metric_alerts(resource, rg, monitor_client):
    return handle_resource(monitor_client.metric_alerts.get, rg, resource)
    
def handle_insights_scheduled_query_rules(resource, rg, monitor_client):
    return handle_resource(monitor_client.scheduled_query_rules.get, rg, resource)
    
def handle_integration_accounts(resource, rg, logic_client):
    return handle_resource(logic_client.integration_accounts.get, rg, resource)
    
def handle_iot_hub(resource, rg, iot_hub_client):
    return handle_resource(iot_hub_client.iot_hub_resource.get, rg, resource)

def handle_key_vault(resource, rg, kv_client):
    return handle_resource(kv_client.vaults.get, rg, resource)

def handle_load_balancer(resource, rg, network_client):
    return handle_resource(network_client.load_balancers.get, rg, resource)

def handle_log_analytics_workspace(resource, rg, la_client):
    return handle_resource(la_client.workspaces.get, rg, resource)

def handle_logic_app(resource, rg, logic_client):
    return handle_resource(logic_client.workflows.get, rg, resource)
    
def handle_monitor_action_group(resource, rg, monitor_client):
    return handle_resource(monitor_client.action_groups.get, rg, resource)

def handle_network_interface(resource, rg, network_client):
    return handle_resource(network_client.network_interfaces.get, rg, resource)

def handle_network_security_group(resource, rg, network_client):
    return handle_resource(network_client.network_security_groups.get, rg, resource)

def handle_private_endpoint(resource, rg, network_client):
    return handle_resource(network_client.private_endpoints.get, rg, resource)

def handle_proximity_placement_group(resource, rg, compute_client):
    return handle_resource(compute_client.proximity_placement_groups.get, rg, resource)

def handle_private_link_services(resource, rg, network_client):
    return handle_resource(network_client.private_link_services.get, rg, resource)

def handle_public_ip(resource, rg, network_client):
    return handle_resource(network_client.public_ip_addresses.get, rg, resource)

def handle_redis_cache(resource, rg, redis_client):
    return handle_resource(redis_client.redis.get, rg, resource)

def handle_restore_point_collections(resource, rg, compute_client):
    return handle_resource(compute_client.restore_point_collections.get, rg, resource)

def handle_route_tables(resource, rg, network_client):
    return handle_resource(network_client.route_tables.get, rg, resource)

def handle_recovery_services_vault(resource, rg, recovery_services_client):
    return handle_resource(recovery_services_client.vaults.get, rg, resource)

def handle_vm_scale_set(resource, rg, compute_client):
    return handle_resource(compute_client.virtual_machine_scale_sets.get, rg, resource)

def handle_scheduler_job_collection(resource, rg, scheduler_client):
    return handle_resource(scheduler_client.job_collections.get, rg, resource)

def handle_search_service(resource, rg, search_client):
    return handle_resource(search_client.services.get, rg, resource)

def handle_service_bus_namespaces(rg, resource, servicebus_client):
    return handle_resource(servicebus_client.namespaces.get, rg, resource)

def handle_service_fabric_cluster(resource, rg, sf_client):
    return handle_resource(sf_client.clusters.get, rg, resource)

def handle_service_endpoint_policy(resource, rg, network_client):
    return handle_resource(network_client.service_endpoint_policies.get, rg, resource)

def handle_signalr_service(resource, rg, signalr_client):
    return handle_resource(signalr_client.signal_r.get, rg, resource)

def handle_smart_detector_alert_rules(resource, rg, alertsmanagement_client):
    return handle_resource(alertsmanagement_client.smart_detector_alert_rules.get, rg, resource)

def handle_sql_migration_services(resource, rg, datamigration_client):
    return handle_resource(datamigration_client.services.get, rg, resource)
    
def handle_sql_managed_instances(resource, rg, sql_client):
    return handle_resource(sql_client.managed_instances.get, rg, resource)
    
def handle_sql_server(resource, rg, sql_client):
    return handle_resource(sql_client.servers.get, rg, resource)

def handle_virtual_cluster(resource, rg, sql_client):
    return handle_resource(sql_client.virtual_clusters.get, rg, resource)

def handle_storage_account(resource, rg, storage_client):
    return handle_resource(storage_client.storage_accounts.get_properties, rg, resource)

def handle_storage_sync_services(resource, rg, storage_sync_client):
    return handle_resource(storage_sync_client.storage_sync_services.get, rg, resource)

def handle_stream_analytics_job(resource, rg, stream_analytics_client):
    return handle_resource(stream_analytics_client.streaming_jobs.get, rg, resource)
    
def handle_traffic_manager(resource, rg, traffic_manager_client):
    return handle_resource(traffic_manager_client.profiles.get, rg, resource)

def handle_virtual_machine(resource, rg, compute_client):
    return handle_resource(compute_client.virtual_machines.get, rg, resource)
    
def handle_vm_images(resource, rg, compute_client):
    return handle_resource(compute_client.images.get, rg, resource)

def handle_vm_snapshot(resource, rg, compute_client):
    return handle_resource(compute_client.snapshots.get, rg, resource)

def handle_vnet(resource, rg, network_client):
    return handle_resource(network_client.virtual_networks.get, rg, resource)

def handle_web_certificate(resource, rg, web_client):
    return handle_resource(web_client.certificates.get, rg, resource)
    
def handle_web_connections(resource, rg, web_client):
    return handle_resource(web_client.web_apps.list_connection_strings, rg, resource)
    
def handle_event_hub_instance(resource, rg, web_client):
    try:
        # Get the Event Hub
        namespace = web_client.namespaces.get(rg.name, resource.name)
        event_hub_instance_list = []
        
        # Get all Event Hubs in the current namespace
        event_hubs = web_client.event_hubs.list_by_namespace(rg.name, namespace.name)
        for event_hub in event_hubs:
                # Convert each Event Hub to a dictionary and add it to the main dictionary
                event_hub_instance_list.append(event_hub.as_dict())
                
        return event_hub_instance_list

    except Exception as e:
        return {'Error': str(e)}
    
def handle_galleries_images_versions(resource, rg, compute_client):
    try:
        # Get the Gallery Image
        gallery_image = compute_client.gallery_images.list_by_gallery(rg.name, resource.name)
        imageversion_list = []
        for gallery in gallery_image:
            gallery_image_versions = compute_client.gallery_image_versions.list_by_gallery_image(rg.name, resource.name, gallery.name)
            # Convert each lock to a dictionary and add it to the main dictionary
            for imageversion in gallery_image_versions:
                imageversion_list.append(imageversion.as_dict())


        return imageversion_list

    except Exception as e:
        return {'Error': str(e)}
    
def handle_galleries_images(resource, rg, compute_client):
    try:
        # Get the Gallery Image
        gallery_image = compute_client.gallery_images.list_by_gallery(rg.name, resource.name)
        gallery_dict = {}
        for gallery in gallery_image:
            # Convert each lock to a dictionary and add it to the main dictionary
            gallery_dict[gallery.name] = gallery.as_dict()

        return gallery_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_management_locks(resource, rg, lock_client):
    try:
        # Get all Management Locks in the resource group
        management_locks = lock_client.management_locks.list_at_resource_group_level(rg)

        # Initialize an empty dictionary to store the Management Locks
        management_locks_dict = {}

        # Iterate over the locks
        for lock in management_locks:
            # Convert each lock to a dictionary and add it to the main dictionary
            management_locks_dict[lock.name] = lock.as_dict()

        return management_locks_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_recovery_services_vault_items(resource, rg, recovery_backup_items_client):
    try:
        # Get all protected items in the vault
        protected_items = recovery_backup_items_client.backup_protected_items.list(resource.name, rg.name)
        
        # Create a dictionary where each key is the item name and the value is the item itself
        protected_items_list = [item.as_dict() for item in protected_items]

        return protected_items_list

    except Exception as e:
        return {'Error': str(e)}
    
def handle_service_bus_queues(rg, resource, servicebus_client):
    try:
        # Get the Service bus instance
        servicebus_namespace = servicebus_client.namespaces.get(resource.name, rg.name)
        
        # Get all Service bus in the current namespace
        service_bus_queues_list = []
        
        queues = servicebus_client.queues.list_by_namespace(resource.name, servicebus_namespace.name)
        # Iterate over the Queues
        for queue in queues:
            # Convert each Queue to a dictionary and add it to the main dictionary
            service_bus_queues_list.append(queue.as_dict())
        
        return service_bus_queues_list

    except Exception as e:
        return {'Error': str(e)}
    
def handle_service_bus_topics(rg, resource, servicebus_client):
    try:
        # Get the Service bus instance
        servicebus_namespace = servicebus_client.namespaces.get(resource.name, rg.name)
        
        # Get all Service bus in the current namespace
        service_bus_topics_list = []
        
        topics = servicebus_client.topics.list_by_namespace(resource.name, servicebus_namespace.name)
        # Iterate over the Queues
        for topic in topics:
            # Convert each Queue to a dictionary and add it to the main list
            service_bus_topics_list.append(topic.as_dict())
        
        return service_bus_topics_list

    except Exception as e:
        return [{'Error': str(e)}]
    
def handle_sql_db(resource, rg, sql_client):
    try:
        # Split the resource id to get the server name
        resource_id_parts = resource.id.split('/')
        server_name = resource_id_parts[resource_id_parts.index('servers') + 1]

        # Get all SQL databases for the given server
        sql_databases = sql_client.databases.list_by_server(rg.name, server_name)

        # Add the details to the sql database dictionary
        sql_databases_dict = [db.as_dict() for db in sql_databases]

        return sql_databases_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_sql_managed_instances_db(resource, rg, sql_client):
    try:
        # Get all SQL databases for the given server
        sql_databases = sql_client.managed_databases.list_by_instance(rg.name, resource.name)

        # Initialize an empty dictionary
        databases_dict = {}

        # Iterate over each database and add it to the dictionary
        for db in sql_databases:
            databases_dict[db.name] = db.as_dict()

        return databases_dict
    except Exception as e:
        return {'Error': str(e)}
    
def handle_all_subnets(resource, rg, network_client):
    try:
        # Get all Virtual Networks in the Resource Group
        vnets = network_client.virtual_networks.get(rg.name, resource.name)
        
        all_subnets = []
        
        # Iterate over each Virtual Network
        for vnet in vnets:
            # Get all Subnets in the current Virtual Network
            subnets = network_client.subnets.list(rg.name, vnet.name)
            
            # Iterate over each Subnet
            for subnet in subnets:
                # Add the keys to the subnet dictionary
                subnet_dict = subnet.as_dict()
                
                # Append the subnet dictionary to the list of all subnets
                all_subnets.append(subnet_dict)
        
        return all_subnets

    except Exception as e:
        return {'Error': str(e)}
    
def handle_virtual_machines_extensions(resource, rg, compute_client):
    try:
        # Get all Virtual Machine Extensions
        vm_extensions = compute_client.virtual_machine_extensions.list(rg.name, resource.name)

        # Create a dictionary where each key is the item name and the value is the item itself
        protected_items_list = [extension.as_dict() for extension in vm_extensions.value]

        return protected_items_list
    
    except Exception as e:
        return {'Error': str(e)}
    
def handle_afd_endpoints(resource, rg, cdn_client):
    try:
        # Get the AFD Endpoint profiles in the rg
        afd_endpointprofile = cdn_client.profiles.get(rg.name, resource.name)

        # Initialize an empty list for storing endpoint dictionaries
        afd_endpoint_dicts = []
        #get individual profiles
        afd_endpoint = cdn_client.endpoints.list_by_profile(resource.name, afd_endpointprofile.name)
        
        # Loop through the iterator
        for endpoint in afd_endpoint:
            # Convert each endpoint to a dictionary and add it to the list
            afd_endpoint_dicts.append(endpoint.as_dict())

        return afd_endpoint_dicts

    except Exception as e:
        return {'Error': str(e)}