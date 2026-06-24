import boto3
from typing import List, Union, Literal
import logging

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(
        self,
        bucket: str = None,
        region: str = None,
        *args,
        **kwargs,
    ):
        self.bucket = bucket
        self.region = region
        self.s3_client = boto3.client("s3")

    def read_from_s3(
        self,
        path: str,
        *,
        bucket: str = None,
        decode: Union[Literal["utf-8"], None] = "utf-8",
    ) -> Union[str, bytes]:
        response = self.s3_client.get_object(
            Bucket=bucket or self.bucket,
            Key=path,
        )
        logger.info(f"Reading file from S3: {path}")
        data: bytes = response["Body"].read()
        return data.decode(decode) if decode else data

    def list_files(
        self,
        *,
        prefix: str,
        bucket: str = None,
    ) -> List[str]:
        paginator = self.s3_client.get_paginator("list_objects_v2")

        files: list[str] = []

        for page in paginator.paginate(Bucket=bucket or self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key: str = obj["Key"]

                filename = (
                    key[len(prefix) + 1 :] if key.startswith(prefix + "/") else key
                )
                files.append(filename)

        return files

    def move_file(
        self,
        source_path: str,
        destination_path: str,
        *,
        bucket: str = None,
    ) -> None:
        logger.info(f"Moving file in S3: {source_path} -> {destination_path}")
        self.s3_client.copy_object(
            Bucket=bucket or self.bucket,
            CopySource={"Bucket": bucket or self.bucket, "Key": source_path},
            Key=destination_path,
        )

        self.s3_client.delete_object(
            Bucket=bucket or self.bucket,
            Key=source_path,
        )

    def delete_file(
        self,
        path: str,
        *,
        bucket: str = None,
    ) -> None:
        logger.info(f"Deleting file from S3: {path}")
        self.s3_client.delete_object(
            Bucket=bucket or self.bucket,
            Key=path,
        )

    def delete_recursively(
        self,
        prefix: str,
        *,
        bucket: str = None,
    ) -> None:
        logger.info(f"Deleting files recursively from S3: {prefix}")
        paginator = self.s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket or self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key: str = obj["Key"]
                self.delete_file(key, bucket=bucket)

    def move_recursively(
        self,
        source_prefix: str,
        destination_prefix: str,
        *,
        bucket: str = None,
    ) -> None:
        logger.info(
            f"Moving files recursively in S3: {source_prefix} -> {destination_prefix}"
        )
        paginator = self.s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=bucket or self.bucket, Prefix=source_prefix
        ):
            for obj in page.get("Contents", []):
                key: str = obj["Key"]
                filename = (
                    key[len(source_prefix) + 1 :]
                    if key.startswith(source_prefix + "/")
                    else key
                )
                destination_path = f"{destination_prefix}/{filename}"
                self.move_file(key, destination_path, bucket=bucket)
