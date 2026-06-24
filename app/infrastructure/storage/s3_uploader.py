import mimetypes
import os
import posixpath
import uuid
from dataclasses import dataclass
from typing import Any
from typing import BinaryIO

from app.core.config import settings
from app.core.exceptions import InfrastructureError
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class UploadedObject:
    key: str
    url: str


class S3Uploader:
    def __init__(
        self,
        *,
        access_key: str,
        secret_key: str,
        region: str,
        bucket_name: str,
        public_base_url: str | None = None,
        use_presigned_urls: bool = False,
        presigned_expires_seconds: int = 3600,
    ) -> None:
        self._bucket_name = bucket_name
        self._region = region
        self._public_base_url = public_base_url.rstrip("/") if public_base_url else None
        self._use_presigned_urls = use_presigned_urls
        self._presigned_expires_seconds = presigned_expires_seconds

        self._client = self._create_client(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
        )

    @staticmethod
    def _create_client(*, access_key: str, secret_key: str, region: str) -> Any:
        try:
            import boto3
        except ModuleNotFoundError as exc:
            raise InfrastructureError(
                code="S3_DEPENDENCY_MISSING",
                message=(
                    "Thiếu dependency S3. Hãy cài boto3 và jmespath trong môi trường chạy ứng dụng."
                ),
            ) from exc

        return boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    @classmethod
    def from_settings(cls) -> "S3Uploader":
        missing: list[str] = []
        if not settings.S3_ACCESS_KEY:
            missing.append("S3_ACCESS_KEY/AWS_ACCESS_KEY")
        if not settings.S3_SECRET_KEY:
            missing.append("S3_SECRET_KEY/AWS_SECRET_KEY")
        if not settings.S3_REGION:
            missing.append("S3_REGION/AWS_REGION")
        if not settings.S3_BUCKET_NAME:
            missing.append("S3_BUCKET_NAME")

        if missing:
            raise InfrastructureError(
                code="S3_CONFIG_MISSING",
                message=f"Thiếu cấu hình S3: {', '.join(missing)}",
            )

        return cls(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            region=settings.S3_REGION,
            bucket_name=settings.S3_BUCKET_NAME,
            public_base_url=settings.S3_PUBLIC_BASE_URL,
            use_presigned_urls=settings.S3_USE_PRESIGNED_URLS,
            presigned_expires_seconds=settings.S3_PRESIGNED_EXPIRES_SECONDS,
        )

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        *,
        filename: str,
        key_prefix: str,
        content_type: str | None = None,
        extra_path: str | None = None,
    ) -> UploadedObject:
        key = self._build_key(
            key_prefix=key_prefix,
            filename=filename,
            extra_path=extra_path,
        )
        resolved_content_type = (
            content_type
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )

        try:
            self._client.upload_fileobj(
                Fileobj=fileobj,
                Bucket=self._bucket_name,
                Key=key,
                ExtraArgs={"ContentType": resolved_content_type},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "s3_upload_failed",
                bucket_name=self._bucket_name,
                key=key,
                content_type=resolved_content_type,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise InfrastructureError(
                code="S3_UPLOAD_FAILED",
                message="Upload S3 thất bại.",
            ) from exc

        return UploadedObject(key=key, url=self.get_object_url(key))

    def get_object_url(self, key: str) -> str:
        if self._use_presigned_urls:
            try:
                return self._client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self._bucket_name, "Key": key},
                    ExpiresIn=self._presigned_expires_seconds,
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "s3_presign_failed",
                    bucket_name=self._bucket_name,
                    key=key,
                    expires_in=self._presigned_expires_seconds,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise InfrastructureError(
                    code="S3_PRESIGN_FAILED",
                    message="Tạo presigned url thất bại.",
                ) from exc

        if self._public_base_url:
            return f"{self._public_base_url}/{key.lstrip('/')}"
        return (
            f"https://{self._bucket_name}.s3.{self._region}.amazonaws.com/{key.lstrip('/')}"
        )

    def _build_key(self, *, key_prefix: str, filename: str, extra_path: str | None) -> str:
        safe_prefix = key_prefix.strip().strip("/")
        safe_extra = (extra_path or "").strip().strip("/")

        _, ext = os.path.splitext(filename)
        ext = ext.lower()[:16]
        object_name = f"{uuid.uuid4().hex}{ext}"

        parts = [p for p in [safe_prefix, safe_extra, object_name] if p]
        return posixpath.join(*parts)
