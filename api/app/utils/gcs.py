"""
Google Cloud Storage helper functions for API
"""
from google.cloud import storage
from google.auth import compute_engine
from google.auth.transport import requests as auth_requests
from google.oauth2 import service_account
from typing import BinaryIO
import logging
import uuid
import datetime
import json
import os

logger = logging.getLogger(__name__)

# Initialize GCS client with service account if available
def _get_storage_client():
    """Get storage client with service account credentials if available"""
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return storage.Client(credentials=credentials)
        except Exception as e:
            logger.warning(f"Failed to load service account from env: {e}")

    # Fallback to default credentials
    return storage.Client()

storage_client = _get_storage_client()


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
    expiration: int = 3600
) -> str:
    """
    Generate signed URL for GCS blob
    Uses service account credentials from environment variable

    Args:
        bucket_name: GCS bucket name
        blob_name: Blob name
        expiration: URL expiration in seconds (default: 1 hour)

    Returns:
        Signed URL
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(seconds=expiration),
            method="GET"
        )

        logger.info(f"Generated signed URL for gs://{bucket_name}/{blob_name}")
        return url

    except AttributeError as e:
        # No private key available - provide helpful error
        logger.error(f"Cannot generate signed URL - no service account key: {str(e)}")
        raise Exception(
            "Cannot generate signed URLs without a service account key. "
            "Please set GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable "
            "with service account JSON key content."
        )
    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}")
        raise
