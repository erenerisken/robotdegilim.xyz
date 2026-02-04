"""Real S3 backend operations."""

from __future__ import annotations

from typing import Any

from app.core.errors import AppError

from .common import _normalize_key, _s3_bucket, get_settings
from .state import get_cached_client, set_cached_client

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:  # pragma: no cover - environments without boto3
    boto3 = None
    ClientError = Exception


def _is_not_found_error(error: Exception) -> bool:
    """Return True when a client error indicates missing key/bucket."""
    if not isinstance(error, ClientError):
        return False
    try:
        code = str(error.response.get("Error", {}).get("Code", ""))
    except Exception:
        return False
    return code in {"404", "NotFound", "NoSuchKey", "NoSuchBucket"}


def _get_s3_client() -> Any:
    """Build and cache boto3 S3 client."""
    client = get_cached_client()
    if client is not None:
        return client
    if boto3 is None:
        raise AppError(
            "boto3 is required when S3_BUCKET is configured.",
            "S3_CLIENT_IMPORT_FAILED",
        )

    try:
        settings = get_settings()
        client_kwargs: dict[str, Any] = {}
        access_key = str(getattr(settings, "S3_ACCESS_KEY_ID", "") or "").strip()
        secret_key = str(getattr(settings, "S3_SECRET_ACCESS_KEY", "") or "").strip()
        if access_key and secret_key:
            client_kwargs["aws_access_key_id"] = access_key
            client_kwargs["aws_secret_access_key"] = secret_key

        client = boto3.client("s3", **client_kwargs)
        set_cached_client(client)
        return client
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to initialize S3 client.",
            "S3_CLIENT_INIT_FAILED",
            cause=e,
        )


def read_object_bytes(key: str) -> bytes | None:
    """Read object bytes from real S3; return None when key is missing."""
    client = _get_s3_client()
    try:
        response = client.get_object(Bucket=_s3_bucket(), Key=_normalize_key(key))
        return bytes(response["Body"].read())
    except Exception as e:
        if _is_not_found_error(e):
            return None
        raise e if isinstance(e, AppError) else AppError(
            "Failed to read object from S3.",
            "S3_READ_FAILED",
            context={"key": key},
            cause=e,
        )


def write_object_bytes(key: str, content: bytes, public_read: bool = False) -> None:
    """Write object bytes to real S3."""
    client = _get_s3_client()
    try:
        put_kwargs: dict[str, Any] = {
            "Bucket": _s3_bucket(),
            "Key": _normalize_key(key),
            "Body": content,
        }
        if public_read:
            put_kwargs["ACL"] = "public-read"
        client.put_object(**put_kwargs)
    except Exception as e:
        if public_read and isinstance(e, ClientError):
            code = str(e.response.get("Error", {}).get("Code", ""))
            if code == "AccessControlListNotSupported":
                raise AppError(
                    "Bucket does not allow ACL-based public reads. Enable ACLs or use a public-read bucket policy.",
                    "S3_PUBLIC_ACL_NOT_SUPPORTED",
                    context={"key": key},
                    cause=e,
                )
        raise e if isinstance(e, AppError) else AppError(
            "Failed to write object to S3.",
            "S3_WRITE_FAILED",
            context={"key": key},
            cause=e,
        )


def object_exists(key: str) -> bool:
    """Check object existence in real S3."""
    client = _get_s3_client()
    try:
        client.head_object(Bucket=_s3_bucket(), Key=_normalize_key(key))
        return True
    except Exception as e:
        if _is_not_found_error(e):
            return False
        raise e if isinstance(e, AppError) else AppError(
            "Failed to check object existence in S3.",
            "S3_EXISTS_FAILED",
            context={"key": key},
            cause=e,
        )


def delete_object(key: str) -> bool:
    """Delete object in real S3 and return whether it existed."""
    client = _get_s3_client()
    existed = object_exists(key)
    if not existed:
        return False
    try:
        client.delete_object(Bucket=_s3_bucket(), Key=_normalize_key(key))
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to delete object from S3.",
            "S3_DELETE_FAILED",
            context={"key": key},
            cause=e,
        )


def reset_cached_client() -> None:
    """Reset cached S3 client reference."""
    set_cached_client(None)
