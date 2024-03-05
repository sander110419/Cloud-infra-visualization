from azure.mgmt.streamanalytics import StreamAnalyticsManagementClient

def handle_stream_analytics_job(resource, rg, stream_analytics_client):
    try:
        # Get the stream_analytics_job
        stream_analytics_job = stream_analytics_client.streaming_jobs.get(rg.name, resource.name)
        print("Getting Stream Analytics Job...")

        # Add the keys to the storage account dictionary
        stream_analytics_job_dict = stream_analytics_job.as_dict()

        return stream_analytics_job_dict

    except Exception as e:
        return {'Error': str(e)}