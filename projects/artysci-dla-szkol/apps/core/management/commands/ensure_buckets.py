"""Create the private and public buckets if missing (S3 backend; MinIO locally and in CI).

Idempotent. The public bucket gets an anonymous read policy; the private one stays closed.
Safe to run against any S3-compatible service the credentials may administer.
"""

import json

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def _options(alias: str) -> dict:
    return settings.STORAGES[alias]["OPTIONS"]


class Command(BaseCommand):
    help = "Create the private/public buckets when STORAGE_BACKEND=s3."

    def handle(self, *args, **options):
        if settings.STORAGE_BACKEND != "s3":
            self.stdout.write("STORAGE_BACKEND is not s3: nothing to do.")
            return
        priv, pub = _options("private"), _options("public")
        client = boto3.client(
            "s3",
            endpoint_url=priv["endpoint_url"],
            aws_access_key_id=priv["access_key"],
            aws_secret_access_key=priv["secret_key"],
            region_name=priv["region_name"],
        )
        for name in (priv["bucket_name"], pub["bucket_name"]):
            try:
                client.head_bucket(Bucket=name)
            except ClientError:
                try:
                    client.create_bucket(Bucket=name)
                except ClientError as exc:
                    raise CommandError(f"Cannot create bucket {name}: {exc}") from exc
                self.stdout.write(f"Created bucket {name}")
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{pub['bucket_name']}/*"],
                }
            ],
        }
        client.put_bucket_policy(Bucket=pub["bucket_name"], Policy=json.dumps(policy))
        self.stdout.write("Buckets ready.")
