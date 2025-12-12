"""
Google Cloud Pub/Sub helper functions
"""
from google.cloud import pubsub_v1
import logging
import json

logger = logging.getLogger(__name__)

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()


async def publish_job(project_id: str, topic_name: str, job_id: str) -> str:
    """
    Publish job to Pub/Sub topic

    Args:
        project_id: GCP project ID
        topic_name: Pub/Sub topic name
        job_id: Job ID to publish

    Returns:
        Message ID
    """
    try:
        topic_path = publisher.topic_path(project_id, topic_name)

        # Encode job_id as bytes
        data = job_id.encode("utf-8")

        # Publish message
        future = publisher.publish(topic_path, data)
        message_id = future.result()

        logger.info(f"Published job {job_id} to {topic_name}, message ID: {message_id}")

        return message_id

    except Exception as e:
        logger.error(f"Error publishing to Pub/Sub: {str(e)}")
        raise
