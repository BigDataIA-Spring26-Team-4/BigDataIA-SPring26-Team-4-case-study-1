from typing import Optional, Dict, List

import boto3
import aioboto3
from botocore.exceptions import ClientError
import structlog

from app.config import get_settings

log = structlog.get_logger(__name__)

# Load settings
settings = get_settings()

# Global S3 clients (initialized lazily)
_s3_client: Optional[boto3.client] = None
_async_s3_session: Optional[aioboto3.Session] = None


def get_s3_client():
    """Get or create synchronous S3 client."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID.get_secret_value(),
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
            region_name=settings.AWS_REGION
        )
        log.info("s3_client_initialized", region=settings.AWS_REGION, bucket=settings.settings.S3_BUCKET_NAME)
    return _s3_client


def get_async_s3_session():
    """Get or create asynchronous S3 session."""
    global _async_s3_session
    if _async_s3_session is None:
        _async_s3_session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID.get_secret_value(),
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
            region_name=settings.AWS_REGION
        )
        log.info("async_s3_session_initialized", region=settings.AWS_REGION, bucket=settings.settings.S3_BUCKET_NAME)
    return _async_s3_session


def upload_document(file_data: bytes, key: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Upload a document to S3 (synchronous).

    Args:
        file_data: Binary content of the file
        key: S3 object key (path/filename in bucket)
        metadata: Optional metadata to attach to the object

    Returns:
        Dict with upload status and object details
    """
    try:
        client = get_s3_client()
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = metadata

        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_data,
            **extra_args
        )

        log.info("document_uploaded", key=key, bucket=settings.S3_BUCKET_NAME, size=len(file_data))
        return {
            "status": "success",
            "key": key,
            "bucket": settings.S3_BUCKET_NAME,
            "size": len(file_data)
        }
    except ClientError as e:
        log.error("document_upload_error", key=key, error=str(e))
        return {"status": "error", "error": str(e)}


async def upload_document_async(file_data: bytes, key: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Upload a document to S3 (asynchronous).

    Args:
        file_data: Binary content of the file
        key: S3 object key (path/filename in bucket)
        metadata: Optional metadata to attach to the object

    Returns:
        Dict with upload status and object details
    """
    try:
        session = get_async_s3_session()
        async with session.client('s3') as client:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata

            await client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=file_data,
                **extra_args
            )

        log.info("document_uploaded_async", key=key, bucket=settings.S3_BUCKET_NAME, size=len(file_data))
        return {
            "status": "success",
            "key": key,
            "bucket": settings.S3_BUCKET_NAME,
            "size": len(file_data)
        }
    except ClientError as e:
        log.error("document_upload_error_async", key=key, error=str(e))
        return {"status": "error", "error": str(e)}


def download_document(key: str) -> Optional[bytes]:
    """Download a document from S3 (synchronous).

    Args:
        key: S3 object key (path/filename in bucket)

    Returns:
        File content as bytes, or None if not found
    """
    try:
        client = get_s3_client()
        response = client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        content = response['Body'].read()

        log.info("document_downloaded", key=key, bucket=settings.S3_BUCKET_NAME, size=len(content))
        return content
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            log.warning("document_not_found", key=key, bucket=settings.S3_BUCKET_NAME)
        else:
            log.error("document_download_error", key=key, error=str(e))
        return None


async def download_document_async(key: str) -> Optional[bytes]:
    """Download a document from S3 (asynchronous).

    Args:
        key: S3 object key (path/filename in bucket)

    Returns:
        File content as bytes, or None if not found
    """
    try:
        session = get_async_s3_session()
        async with session.client('s3') as client:
            response = await client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            async with response['Body'] as stream:
                content = await stream.read()

        log.info("document_downloaded_async", key=key, bucket=settings.S3_BUCKET_NAME, size=len(content))
        return content
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            log.warning("document_not_found_async", key=key, bucket=settings.S3_BUCKET_NAME)
        else:
            log.error("document_download_error_async", key=key, error=str(e))
        return None


def delete_document(key: str) -> Dict[str, str]:
    """Delete a document from S3 (synchronous).

    Args:
        key: S3 object key (path/filename in bucket)

    Returns:
        Dict with deletion status
    """
    try:
        client = get_s3_client()
        client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)

        log.info("document_deleted", key=key, bucket=settings.S3_BUCKET_NAME)
        return {"status": "success", "key": key}
    except ClientError as e:
        log.error("document_delete_error", key=key, error=str(e))
        return {"status": "error", "error": str(e)}


async def delete_document_async(key: str) -> Dict[str, str]:
    """Delete a document from S3 (asynchronous).

    Args:
        key: S3 object key (path/filename in bucket)

    Returns:
        Dict with deletion status
    """
    try:
        session = get_async_s3_session()
        async with session.client('s3') as client:
            await client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)

        log.info("document_deleted_async", key=key, bucket=settings.S3_BUCKET_NAME)
        return {"status": "success", "key": key}
    except ClientError as e:
        log.error("document_delete_error_async", key=key, error=str(e))
        return {"status": "error", "error": str(e)}


def list_documents(prefix: str = "", max_keys: int = 1000) -> List[Dict[str, any]]:
    """List documents in S3 bucket (synchronous).

    Args:
        prefix: Filter objects by prefix (folder path)
        max_keys: Maximum number of keys to return

    Returns:
        List of objects with key, size, and last_modified
    """
    try:
        client = get_s3_client()
        response = client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_keys
        )

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })

        log.info("documents_listed", prefix=prefix, count=len(objects))
        return objects
    except ClientError as e:
        log.error("document_list_error", prefix=prefix, error=str(e))
        return []


async def list_documents_async(prefix: str = "", max_keys: int = 1000) -> List[Dict[str, any]]:
    """List documents in S3 bucket (asynchronous).

    Args:
        prefix: Filter objects by prefix (folder path)
        max_keys: Maximum number of keys to return

    Returns:
        List of objects with key, size, and last_modified
    """
    try:
        session = get_async_s3_session()
        async with session.client('s3') as client:
            response = await client.list_objects_v2(
                Bucket=settings.S3_BUCKET_NAME,
                Prefix=prefix,
                MaxKeys=max_keys
            )

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })

        log.info("documents_listed_async", prefix=prefix, count=len(objects))
        return objects
    except ClientError as e:
        log.error("document_list_error_async", prefix=prefix, error=str(e))
        return []


def get_document_metadata(key: str) -> Optional[Dict[str, any]]:
    """Get metadata for a document in S3 (synchronous).

    Args:
        key: S3 object key (path/filename in bucket)

    Returns:
        Dict with object metadata or None if not found
    """
    try:
        client = get_s3_client()
        response = client.head_object(Bucket=settings.S3_BUCKET_NAME, Key=key)

        metadata = {
            'key': key,
            'size': response['ContentLength'],
            'content_type': response.get('ContentType'),
            'last_modified': response['LastModified'].isoformat(),
            'metadata': response.get('Metadata', {})
        }

        log.info("document_metadata_retrieved", key=key)
        return metadata
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            log.warning("document_not_found_metadata", key=key)
        else:
            log.error("document_metadata_error", key=key, error=str(e))
        return None


async def get_document_metadata_async(key: str) -> Optional[Dict[str, any]]:
    """Get metadata for a document in S3 (asynchronous).

    Args:
        key: S3 object key (path/filename in bucket)

    Returns:
        Dict with object metadata or None if not found
    """
    try:
        session = get_async_s3_session()
        async with session.client('s3') as client:
            response = await client.head_object(Bucket=settings.S3_BUCKET_NAME, Key=key)

        metadata = {
            'key': key,
            'size': response['ContentLength'],
            'content_type': response.get('ContentType'),
            'last_modified': response['LastModified'].isoformat(),
            'metadata': response.get('Metadata', {})
        }

        log.info("document_metadata_retrieved_async", key=key)
        return metadata
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            log.warning("document_not_found_metadata_async", key=key)
        else:
            log.error("document_metadata_error_async", key=key, error=str(e))
        return None


async def check_s3() -> dict:
    """Check S3 connectivity and bucket access."""
    try:
        session = get_async_s3_session()
        async with session.client('s3') as client:
            # Try to head the bucket to verify access
            await client.head_bucket(Bucket=settings.S3_BUCKET_NAME)

        log.debug("s3_health_check_ok", bucket=settings.S3_BUCKET_NAME)
        return {"status": "ok", "bucket": settings.S3_BUCKET_NAME, "error": None}
    except ClientError as e:
        log.error("s3_health_check_error", bucket=settings.S3_BUCKET_NAME, error=str(e))
        return {"status": "error", "bucket": settings.S3_BUCKET_NAME, "error": str(e)}
    except Exception as e:
        log.error("s3_health_check_unexpected_error", error=str(e))
        return {"status": "error", "error": str(e)}
