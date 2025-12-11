"""
Google Cloud Storage helper functions
"""
from google.cloud import storage
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

# Initialize GCS client
storage_client = storage.Client()


async def download_from_gcs(bucket_name: str, blob_name: str, local_path: str) -> str:
    """
    Download file from GCS to local path

    Args:
        bucket_name: GCS bucket name
        blob_name: Blob name (file path in bucket)
        local_path: Local file path to save to

    Returns:
        Local file path
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        blob.download_to_filename(local_path)
        logger.info(f"Downloaded gs://{bucket_name}/{blob_name} to {local_path}")

        return local_path

    except Exception as e:
        logger.error(f"Error downloading from GCS: {str(e)}")
        raise


async def upload_to_gcs(local_path: str, bucket_name: str, blob_name: str) -> str:
    """
    Upload file from local path to GCS

    Args:
        local_path: Local file path
        bucket_name: GCS bucket name
        blob_name: Blob name (file path in bucket)

    Returns:
        GCS URL (gs://bucket/blob)
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(local_path)
        logger.info(f"Uploaded {local_path} to gs://{bucket_name}/{blob_name}")

        return f"gs://{bucket_name}/{blob_name}"

    except Exception as e:
        logger.error(f"Error uploading to GCS: {str(e)}")
        raise


async def get_signed_url(bucket_name: str, blob_name: str, expiration: int = 900) -> str:
    """
    Generate signed URL for GCS blob

    Args:
        bucket_name: GCS bucket name
        blob_name: Blob name
        expiration: URL expiration in seconds (default: 15 minutes)

    Returns:
        Signed URL
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )

        return url

    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}")
        raise
