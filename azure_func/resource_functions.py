
def handle_container_registry(resource, rg, container_registry_client):
    try:
        # Get the container registry
        container_registry = container_registry_client.registries.get(rg.name, resource.name)

        # Add the keys to the container registry dictionary
        container_registry_dict = container_registry.as_dict()

        return container_registry_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_action_rules(resource, rg, alertsmanagement_client):
    try:

        # Get the Action Rule
        action_rule = alertsmanagement_client.action_rules.get_by_name(rg.name, resource.name)

        # Add the keys to the Action Rule dictionary
        action_rule_dict = action_rule.as_dict()
        return action_rule_dict

    except Exception as e:
        #print(f"Error: {e}")
        return {'Error': str(e)}

# def handle_afd_endpoints(resource, rg, cdn_client):
#     try:
#         # Get the AFD Endpoint profiles in the rg
#         afd_endpointprofile = cdn_client.ProfilesOperations.list_by_resource_group(rg.name)
#         # Initialize an empty list for storing endpoint dictionaries
#         afd_endpoint_dicts = []
#         #get individual profiles
#         for endpointprofile in afd_endpointprofile:
#             afd_endpoint = cdn_client.afd_endpoints.list_by_profile(rg.name, endpointprofile.name)
            
#             # Loop through the iterator
#             for endpoint in afd_endpoint:
#                 # Convert each endpoint to a dictionary and add it to the list
#                 afd_endpoint_dicts.append(endpoint.as_dict())

#         return afd_endpoint_dicts

#     except Exception as e:
#         return {'Error': str(e)}

def handle_aks_service(resource, rg, aks_client):
    try:
        # Get the AKS
        aks_service = aks_client.managed_clusters.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        aks_service_dict = aks_service.as_dict()

        return aks_service_dict

    except Exception as e:
        return {'Error': str(e)}

def handle_api_management(resource, rg, apim_client):
    # Get the API Management
    try:
        # Get the API Management
        api_management = apim_client.api_management_service.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        api_management_dict = api_management.as_dict()

        return api_management_dict

    except Exception as e:
        return {'Error': str(e)}
    

# def handle_application_gateway_waf_policies(resource, rg, network_client):
#     try:
#         # Get the Application Gateway WAF Policy
#         waf_policy = network_client.application_gateway_waf_policies.get(rg.name, resource.name)

#         # Add the keys to the WAF policy dictionary
#         waf_policy_dict = waf_policy.as_dict()

#         return waf_policy_dict

#     except Exception as e:
#         return {'Error': str(e)}
    
def handle_app_service_plan(resource, rg, web_client):
    try:
        # Get the app service plan
        app_service_plan = web_client.app_service_plans.get(rg.name, resource.name)

        # Add the keys to the app service plan dictionary
        app_service_plan_dict = app_service_plan.as_dict()

        return app_service_plan_dict

    except Exception as e:
        return {'Error': str(e)}

def handle_appservices(resource, rg, web_client):
    try:
        # Get the app services
        app_services = web_client.web_apps.get(rg.name, resource.name)

        # Add the details to the app service dictionary
        app_services_dict = app_services.as_dict()

        return app_services_dict

    except Exception as e:
        return {'Error': str(e)}

def handle_batch_account(resource, rg, batch_client):
    try:
        # Get the Batch Account
        batch_account = batch_client.batch_account.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        batch_account_dict = batch_account.as_dict()

        return batch_account_dict

    except Exception as e:
        return {'Error': str(e)}

def handle_bot_service(resource, rg, bot_service_client):
    try:
        # Get the Bot Service
        bot_service = bot_service_client.bots.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        bot_service_dict = bot_service.as_dict()

        return bot_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_cdn_profile(resource, rg, cdn_client):
    try:
        # Get the CDN profile
       cdn_profile = cdn_client.profiles.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       cdn_profile_dict = cdn_profile.as_dict()

       return cdn_profile_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_instance(resource, rg, container_instance_client):
    try:
        # Get the container instance
        container_instance = container_instance_client.container_groups.get(rg.name, resource.name)

        # Add the keys to the container instance dictionary
        container_instance_dict = container_instance.as_dict()

        return container_instance_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_cognitive_service(resource, rg, cognitive_client):
    try:
        # Get the cognitive_service
       cognitive_service = cognitive_client.accounts.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       cognitive_service_dict = cognitive_service.as_dict()

       return cognitive_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_communication_services(resource, rg, communication_client):
    try:
        communication_services = communication_client.communication_services.get(rg.name, resource.name)
        
        communication_services_dict = communication_services.as_dict()
        return communication_services_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_app(resource, rg, container_client):
    try:
        # Get the Container App
        container_app = container_client.container_groups.get(rg.name, resource.name)

        # Add the keys to the Container App dictionary
        container_app_dict = container_app.as_dict()

        return container_app_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_images(resource, rg, container_registry_client):
    try:
        # Get the Container Image
        container_image = container_registry_client.container_images.get(rg.name, resource.name)

        # Add the keys to the Container Image dictionary
        container_image_dict = container_image.as_dict()

        return container_image_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_registry(resource, rg, container_registry_client):
    try:
        # Get the Container Registry
       container_registry = container_registry_client.registries.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       container_registry_dict = container_registry.as_dict()

       return container_registry_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_cosmosdb_account(resource, rg, cosmosdb_client):
    try:
        # Get the cosmosdb
       cosmosdb_account = cosmosdb_client.database_accounts.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       cosmosdb_account_dict = cosmosdb_account.as_dict()

       return cosmosdb_account_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_batch_account(resource, rg, batch_client):
    try:
        # Get the Batch Account
        batch_account = batch_client.batch_account.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        batch_account_dict = batch_account.as_dict()

        return batch_account_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_bot_service(resource, rg, bot_service_client):
    try:
        # Get the Bot Service
        bot_service = bot_service_client.bots.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        bot_service_dict = bot_service.as_dict()

        return bot_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_cdn_profile(resource, rg, cdn_client):
    try:
        # Get the CDN profile
       cdn_profile = cdn_client.profiles.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       cdn_profile_dict = cdn_profile.as_dict()

       return cdn_profile_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_instance(resource, rg, container_instance_client):
    try:
        # Get the container instance
        container_instance = container_instance_client.container_groups.get(rg.name, resource.name)

        # Add the keys to the container instance dictionary
        container_instance_dict = container_instance.as_dict()

        return container_instance_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_cognitive_service(resource, rg, cognitive_client):
    try:
        # Get the cognitive_service
       cognitive_service = cognitive_client.accounts.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       cognitive_service_dict = cognitive_service.as_dict()

       return cognitive_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_app(resource, rg, containerapp_client):
    try:
        # Get the Container App
        container_app = containerapp_client.container_apps.get(rg, resource)

        # Add the keys to the Container App dictionary
        container_app_dict = container_app.as_dict()

        return container_app_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_images(resource, rg, container_registry_client):
    try:
        # Get the Container Image
        container_image = container_registry_client.container_images.get(rg.name, resource.name)

        # Add the keys to the Container Image dictionary
        container_image_dict = container_image.as_dict()

        return container_image_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_container_registry(resource, rg, container_registry_client):
    try:
        # Get the Container Registry
       container_registry = container_registry_client.registries.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       container_registry_dict = container_registry.as_dict()

       return container_registry_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_cosmosdb_account(resource, rg, cosmosdb_client):
    try:
        # Get the cosmosdb
       cosmosdb_account = cosmosdb_client.database_accounts.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
       cosmosdb_account_dict = cosmosdb_account.as_dict()

       return cosmosdb_account_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_data_factory(resource, rg, data_factory_client):
    try:
        # Get the Data Factory
        data_factory = data_factory_client.factories.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        data_factory_dict = data_factory.as_dict()

        return data_factory_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_data_lake_store(resource, rg, datalake_store_client):
    try:
       # Get the Data Lake Store
        data_lake_store = datalake_store_client.account.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        data_lake_store_dict = data_lake_store.as_dict()

        return data_lake_store_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_devtest_lab(resource, rg, devtest_client):
    try:
       # Get the devtest_lab
        devtest_lab = devtest_client.labs.get(rg.name, resource.name)


        # Add the keys to the storage account dictionary
        devtest_lab_dict = devtest_lab.as_dict()

        return devtest_lab_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_disk(resource, rg, compute_client):
    try:
       # Get the Disk
        disk = compute_client.disks.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        disk_dict = disk.as_dict()

        return disk_dict

    except Exception as e:
        return {'Error': str(e)}
    
# def handle_private_dns_zones(resource, rg, network_client):
#     try:
#         # Get the Private DNS Zone
#         private_dns_zone = network_client.private_dns_zones.get(rg.name, resource.name)

#         # Add the keys to the Private DNS Zone dictionary
#         private_dns_zone_dict = private_dns_zone.as_dict()

#         return private_dns_zone_dict

#     except Exception as e:
#         return {'Error': str(e)}
    
def handle_event_grids(resource, rg, event_grid_client):
    try:
        # Get the Event Grid Topic
        event_grid_topic = event_grid_client.topics.get(rg.name, resource.name)

        # Add the keys to the Event Grid Topic dictionary
        event_grid_dict = event_grid_topic.as_dict()

        return event_grid_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_event_grid_subscriptions(resource, rg, event_grid_client):
    try:
        # Get the Event Grid Subscription
        event_grid_subscription = event_grid_client.event_subscriptions.get(rg.name, resource.name)

        # Add the keys to the Event Grid Subscription dictionary
        event_grid_dict = event_grid_subscription.as_dict()

        return event_grid_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_event_hub_instance(resource, rg, web_client):
    try:
       # Get the Event Hub
        namespace = web_client.namespaces.get(rg, resource)
        event_hub_instance_list = []
        #print("Getting Event Hub namespaces...")
        
        # Get all Event Hubs in the current namespace
        event_hubs = web_client.event_hubs.list_by_namespace(rg.name, namespace.name)
        for event_hub in event_hubs:
                # Convert each Event Hub to a dictionary and add it to the main dictionary
                event_hub_instance_list.append(event_hub.as_dict())
                
        return event_hub_instance_list

    except Exception as e:
        return {'Error': str(e)}
    
def handle_event_hub_namespaces(resource, rg, eventhub_client):
    try:
       # Get the Event Hub
        namespaces = eventhub_client.namespaces.get(rg.name, resource.name)

        namespaces_dict = namespaces.as_dict()

        return namespaces_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_galleries_images_versions(resource, rg, compute_client):
    try:
        # Get the Gallery Image
        gallery_image = compute_client.gallery_images.list_by_gallery(rg, resource)
        imageversion_dict = {}
        for gallery in gallery_image:
            gallery_image_versions = compute_client.gallery_image_versions.list_by_gallery_image(rg, resource, gallery.name)
            # Convert each lock to a dictionary and add it to the main dictionary
            for imageversion in gallery_image_versions:
                imageversion_dict[imageversion.name] = imageversion.as_dict()


        return imageversion_dict

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


def handle_image_galleries(resource, rg, compute_client):
    try:
        # Get the Image Gallery
        image_gallery = compute_client.galleries.get(rg.name, resource.name)

        # Add the keys to the Image Gallery dictionary
        image_gallery_dict = image_gallery.as_dict()

        return image_gallery_dict

    except Exception as e:
        return {'Error': str(e)}
    
# def handle_insights_components(resource, rg, monitor_client):
#     try:
#         # Get the Insights Component
#         insights_component = monitor_client.components.get(rg.name, resource.name)

#         # Add the keys to the insights component dictionary
#         insights_component_dict = insights_component.as_dict()

#         return insights_component_dict

#     except Exception as e:
#         return {'Error': str(e)}
    
def handle_insights_metric_alerts(resource, rg, monitor_client):
    try:
        # Get the Metric Alert
        metric_alert = monitor_client.metric_alerts.get(rg.name, resource.name)

        # Add the keys to the metric alert dictionary
        metric_alert_dict = metric_alert.as_dict()

        return metric_alert_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_insights_scheduled_query_rules(resource, rg, monitor_client):
    try:
        # Get the Scheduled Query Rule
        scheduled_query_rule = monitor_client.scheduled_query_rules.get(rg.name, resource.name)

        # Add the keys to the scheduled query rule dictionary
        scheduled_query_rule_dict = scheduled_query_rule.as_dict()

        return scheduled_query_rule_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_integration_accounts(resource, rg, logic_client):
    try:
        integration_account = logic_client.integration_accounts.get(rg.name, resource.name)
        integration_account_dict = integration_account.as_dict()

        return integration_account_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_iot_hub(resource, rg, iot_hub_client):
    try:
       # Get the IoT Hub
        iot_hub = iot_hub_client.iot_hub_resource.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        iot_hub_dict = iot_hub.as_dict()

        return iot_hub_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_key_vault(resource, rg, kv_client):
    try:
       # Get the key_vault
        key_vault = kv_client.vaults.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        key_vault_dict = key_vault.as_dict()

        return key_vault_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_load_balancer(resource, rg, network_client):
    try:
       # Get the Load Balancer
        load_balancer = network_client.load_balancers.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        load_balancer_dict = load_balancer.as_dict()

        return load_balancer_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_log_analytics_workspace(resource, rg, la_client):
    try:
        # Get the log analytics workspace
        log_analytics_workspace = la_client.workspaces.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        log_analytics_workspace_dict = log_analytics_workspace.as_dict()

        return log_analytics_workspace_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_logic_app(resource, rg, logic_client):
    try:
        # Get the Logic App
        logic_app = logic_client.workflows.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        logic_app_dict = logic_app.as_dict()

        return logic_app_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_management_locks(resource, rg, lock_client):
    try:
        # Get all Management Locks in the resource group
        management_locks = lock_client.management_locks.list_at_resource_group_level(rg)

        #print(management_locks)

        # Initialize an empty dictionary to store the Management Locks
        management_locks_dict = {}

        # Iterate over the locks
        for lock in management_locks:
            # Convert each lock to a dictionary and add it to the main dictionary
            management_locks_dict[lock.name] = lock.as_dict()

        return management_locks_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_monitor_action_group(resource, rg, monitor_client):
    try:
        # Get the Action Group
        action_group = monitor_client.action_groups.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        action_group_dict = action_group.as_dict()

        return action_group_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_network_interface(resource, rg, network_client):
    try:
        # Get the nic
        nic = network_client.network_interfaces.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        nic_dict = nic.as_dict()

        return nic_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_network_security_group(resource, rg, network_client):
    try:
        # Get the Network Security Group
        network_security_group = network_client.network_security_groups.get(rg.name, resource.name)

        # Add the keys to the Network Security Group dictionary
        network_security_group_dict = network_security_group.as_dict()

        return network_security_group_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_private_endpoint(resource, rg, network_client):
    try:
        # Get the Private Endpoint
        private_endpoint = network_client.private_endpoints.get(rg.name, resource.name)

        # Add the keys to the Private Endpoint dictionary
        private_endpoint_dict = private_endpoint.as_dict()

        return private_endpoint_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_proximity_placement_group(resource, rg, compute_client):
    try:
        # Get the Proximity Placement Group
        proximity_placement_group = compute_client.proximity_placement_groups.get(rg.name, resource.name)

        # Add the keys to the Proximity Placement Group dictionary
        proximity_placement_group_dict = proximity_placement_group.as_dict()

        return proximity_placement_group_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_private_link_services(resource, rg, network_client):
    try:
        private_link_service = network_client.private_link_services.get(rg.name, resource.name)
        private_link_service_dict = private_link_service.as_dict()

        return private_link_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_public_ip(resource, rg, network_client):
    try:
        # Get the public ip address
        public_ip = network_client.public_ip_addresses.get(rg.name, resource.name)

        # Add the keys to the public ip address dictionary
        public_ip_dict = public_ip.as_dict()

        return public_ip_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_redis_cache(resource, rg, redis_client):
    try:
        # Get the Redis Cache
        redis_cache = redis_client.redis.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        redis_cache_dict = redis_cache.as_dict()

        return redis_cache_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_restore_point_collections(resource, rg, compute_client):
    try:
        restore_point_collection = compute_client.restore_point_collections.get(rg.name, resource.name)
        restore_point_collection_dict = restore_point_collection.as_dict()

        return restore_point_collection_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_route_tables(resource, rg, network_client):
    try:
        # Get the Route Table
        route_table = network_client.route_tables.get(rg.name, resource.name)

        # Add the keys to the Route Table dictionary
        route_table_dict = route_table.as_dict()

        return route_table_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_recovery_services_vault(resource, rg, recovery_services_client):
    try:
        # Get the recovery services vault
        recovery_services_vault = recovery_services_client.vaults.get(rg.name, resource.name)

        # Add the keys to the recovery services vault dictionary
        recovery_services_vault_dict = recovery_services_vault.as_dict()
        #print(recovery_services_vault_dict)

        return recovery_services_vault_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_recovery_services_vault_items(resource, rg, recovery_backup_items_client):
    try:
        # Get all protected items in the vault
        protected_items = recovery_backup_items_client.backup_protected_items.list(resource.name, rg.name)
        
        # Create a dictionary where each key is the item name and the value is the item itself
        protected_items_list = [item.as_dict() for item in protected_items]
        #print(protected_items_dict)

        return protected_items_list

    except Exception as e:
        return {'Error': str(e)}

def handle_vm_scale_set(resource, rg, compute_client):
    try:
        # Get the Virtual Machine Scale Set
        vm_scale_set = compute_client.virtual_machine_scale_sets.get(rg.name, resource.name)

        # Add the keys to the VM Scale Set dictionary
        vm_scale_set_dict = vm_scale_set.as_dict()

        return vm_scale_set_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_scheduler_job_collection(resource, rg, scheduler_client):
    try:
        # Get the Scheduler
        job_collection = scheduler_client.job_collections.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        job_collection_dict = job_collection.as_dict()

        return job_collection_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_search_service(resource, rg, search_client):
    try:
        # Get the Search Service
        search_service = search_client.services.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        search_service_dict = search_service.as_dict()

        return search_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_service_bus_namespaces(rg, resource, servicebus_client):
    try:
        # Get the Service bus instance
        servicebus_namespace = servicebus_client.namespaces.get(resource.name, rg.name)
        
        # Get all Service bus in the current namespace
        servicebus_namespaces_dict = servicebus_namespace.as_dict()
        
        return servicebus_namespaces_dict

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

def handle_service_fabric_cluster(resource, rg, sf_client):
    try:
        # Get the service_fabric
        sf_cluster = sf_client.clusters.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        sf_cluster_dict = sf_cluster.as_dict()

        return sf_cluster_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_service_endpoint_policy(resource, rg, network_client):
    try:
        service_endpoint_policy = network_client.service_endpoint_policies.get(rg.name, resource.name)

        # Add the keys to the service endpoint policy dictionary
        service_endpoint_policy_dict = service_endpoint_policy.as_dict()

        return service_endpoint_policy_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_signalr_service(resource, rg, signalr_client):
    try:
        # Get the signalr_service
        signalr_service = signalr_client.signal_r.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        signalr_service_dict = signalr_service.as_dict()

        return signalr_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_smart_detector_alert_rules(resource, rg, alertsmanagement_client):
    try:
        # Get the Smart Detector Alert Rule
        alert_rule = alertsmanagement_client.smart_detector_alert_rules.get(rg.name, resource.name)

        # Add the keys to the Smart Detector Alert Rule dictionary
        alert_rule_dict = alert_rule.as_dict()

        return alert_rule_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_sql_migration_services(resource, rg, datamigration_client):
    try:
        sql_migration_services = datamigration_client.services.get(rg.name, resource.name)
        
        sql_migration_services_dict = sql_migration_services.as_dict()
        return sql_migration_services_dict

    except Exception as e:
        return {'Error': str(e)}
    
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
    
def handle_sql_managed_instances(resource, rg, sql_client):
    try:
        sql_managed_instance = sql_client.managed_instances.get(rg.name, resource.name)
        sql_managed_instance_dict = sql_managed_instance.as_dict()

        return sql_managed_instance_dict

    except Exception as e:
        return {'Error': str(e)}
    
# def handle_sql_managed_instances_db(resource, rg, sql_client):
#     try:
#         # Split the resource id to get the server name
#         resource_id_parts = resource.id.split('/')
#         server_name = resource_id_parts[resource_id_parts.index('servers') + 1]

#         # Get all SQL databases for the given server
#         sql_databases = sql_client.databases.list_by_instance(rg.name, server_name)

#         # Initialize an empty dictionary
#         databases_dict = {}

#         # Iterate over each database and add it to the dictionary
#         for db in sql_databases:
#             databases_dict[db.name] = db.as_dict()

#         return databases_dict
#     except Exception as e:
#         return {'Error': str(e)}
    
def handle_sql_server(resource, rg, sql_client):
    try:
        # Get the sql_server
        server = sql_client.servers.get(rg.name, resource.name)

        # Add the keys to the app service plan dictionary
        server_dict = server.as_dict()

        return server_dict

    except Exception as e:
        return {'Error': str(e)}
    

def handle_virtual_cluster(resource, rg, sql_client):
    try:
        virtual_cluster = sql_client.virtual_clusters.get(rg.name, resource.name)
        virtual_cluster_dict = virtual_cluster.as_dict()

        return virtual_cluster_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_storage_account(resource, rg, storage_client):
    try:
        # Get the storage account
        storage_account = storage_client.storage_accounts.get_properties(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        storage_account_dict = storage_account.as_dict()

        return storage_account_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_storage_sync_services(resource, rg, storage_sync_client):
    try:
        storage_sync_service = storage_sync_client.storage_sync_services.get(rg.name, resource.name)
        storage_sync_service_dict = storage_sync_service.as_dict()

        return storage_sync_service_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_stream_analytics_job(resource, rg, stream_analytics_client):
    try:
        # Get the stream_analytics_job
        stream_analytics_job = stream_analytics_client.streaming_jobs.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        stream_analytics_job_dict = stream_analytics_job.as_dict()

        return stream_analytics_job_dict

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
    
def handle_traffic_manager(resource, rg, traffic_manager_client):
    try:
        # Get the Traffic Manager
        traffic_manager = traffic_manager_client.profiles.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        traffic_manager_dict = traffic_manager.as_dict()

        return traffic_manager_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_virtual_machine(resource, rg, compute_client):
    try:
        # Get the VM
        vm = compute_client.virtual_machines.get(rg.name, resource.name)

        # Add the keys to the storage account dictionary
        vm_dict = vm.as_dict()

        return vm_dict

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
    
def handle_vm_images(resource, rg, compute_client):
    try:
        # Get the VM Image
        vm_image = compute_client.images.get(rg.name, resource.name)

        # Add the keys to the VM Image dictionary
        vm_image_dict = vm_image.as_dict()

        return vm_image_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_vm_snapshot(resource, rg, compute_client):
    try:
        # Get the VM snapshot
        vm_snapshot = compute_client.snapshots.get(rg.name, resource.name)

        # Add the keys to the snapshot dictionary
        vm_snapshot_dict = vm_snapshot.as_dict()

        return vm_snapshot_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_vnet(resource, rg, network_client):
    try:
        # Get the Virtual Network
        vnet = network_client.virtual_networks.get(rg.name, resource.name)

        # Add the keys to the vnet dictionary
        vnet_dict = vnet.as_dict()

        return vnet_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_web_certificate(resource, rg, web_client):
    try:
        # Get the web certificate
        certificate = web_client.certificates.get(rg.name, resource.name)

        # Add the keys to the web certificate dictionary
        certificate_dict = certificate.as_dict()

        return certificate_dict

    except Exception as e:
        return {'Error': str(e)}
    
def handle_web_connections(resource, rg, web_client):
    try:
        connection = web_client.web_apps.list_connection_strings(rg.name, resource.name)
        connection_dict = {conn_str.name: conn_str.connection_string for conn_str in connection.value}

        return connection_dict

    except Exception as e:
        return {'Error': str(e)}