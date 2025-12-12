"""
Google Cloud Storage helper functions for API
"""
from google.cloud import storage
from typing import BinaryIO
import logging
import uuid

logger = logging.getLogger(__name__)

# Initialize GCS client
storage_client = storage.Client()


async def upload_to_gcs(
    file: BinaryIO,
    bucket_name: str,
    blob_name: str,
    content_type: str = "image/jpeg"
) -> str:
    """
    Upload file to GCS

    Args:
        file: File object to upload
        bucket_name: GCS bucket name
        blob_name: Blob name (file path in bucket)
        content_type: MIME type

    Returns:
        GCS URL (gs://bucket/blob)
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_file(file, content_type=content_type, rewind=True)
        logger.info(f"Uploaded to gs://{bucket_name}/{blob_name}")

        return f"gs://{bucket_name}/{blob_name}"

    except Exception as e:
        logger.error(f"Error uploading to GCS: {str(e)}")
        raise


async def get_signed_url(
    bucket_name: str,
    blob_name: str,
    expiration: int = 900
) -> str:
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
