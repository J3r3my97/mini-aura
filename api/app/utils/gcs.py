"""
Google Cloud Storage helper functions for API
"""
from google.cloud import storage
from google.auth import compute_engine
from google.auth.transport import requests as auth_requests
from typing import BinaryIO
import logging
import uuid
import datetime

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
    expiration: int = 3600
) -> str:
    """
    Generate signed URL for GCS blob using service account impersonation
    Works on Cloud Run without needing a private key file

    Args:
        bucket_name: GCS bucket name
        blob_name: Blob name
        expiration: URL expiration in seconds (default: 1 hour)

    Returns:
        Signed URL
    """
    try:
        from google.auth import iam
        from google.auth.transport import requests as google_requests
        import google.auth

        # Get default credentials (works on Cloud Run)
        credentials, project_id = google.auth.default()

        # Create request object
        request = google_requests.Request()

        # Get service account email from metadata (Cloud Run)
        try:
            service_account_email = credentials.service_account_email
        except AttributeError:
            # Fallback: use default compute service account
            import os
            project_id = os.getenv("PROJECT_ID", "mini-aura")
            service_account_email = f"{project_id}@appspot.gserviceaccount.com"

        # Use IAM signBlob API to generate signed URL without private key
        signing_credentials = iam.Signer(
            request,
            credentials,
            service_account_email
        )

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Generate signed URL using IAM-based signing
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(seconds=expiration),
            method="GET",
            credentials=signing_credentials
        )

        logger.info(f"Generated signed URL for gs://{bucket_name}/{blob_name}")
        return url

    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}")

        # Fallback: try to make blob public and return public URL
        try:
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.make_public()
            public_url = blob.public_url
            logger.warning(f"Falling back to public URL: {public_url}")
            return public_url
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            raise e
