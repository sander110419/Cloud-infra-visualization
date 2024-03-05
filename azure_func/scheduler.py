from azure.mgmt.scheduler import SchedulerManagementClient

def handle_scheduler_job_collection(resource, rg, scheduler_client):
    try:
        # Get the Scheduler
        job_collection = scheduler_client.job_collections.get(rg.name, resource.name)
        print("Getting Scheduler...")

        # Add the keys to the storage account dictionary
        job_collection_dict = job_collection.as_dict()

        return job_collection_dict

    except Exception as e:
        return {'Error': str(e)}