import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../.."
        )
    )
)

import boto3
import pytest

import backup


@pytest.fixture
def s3_client():
    """
    Create an S3 client connected to LocalStack.
    """

    return boto3.client(
        "s3",
        endpoint_url=backup.S3_ENDPOINT_URL,
        aws_access_key_id=backup.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=backup.AWS_SECRET_ACCESS_KEY,
        region_name=backup.AWS_REGION,
    )


def test_s3_bucket_exists(s3_client):
    """
    Verify that the configured S3 bucket exists.
    """

    response = s3_client.list_buckets()

    buckets = [
        bucket["Name"]
        for bucket in response["Buckets"]
    ]

    assert backup.S3_BUCKET_NAME in buckets


def test_upload_backup_to_localstack(s3_client, tmp_path):
    """
    Verify that a backup file can be uploaded to LocalStack S3.
    """

    # Create a fake backup file.
    backup_file = tmp_path / "integration_test.tar.gz"
    backup_file.write_text("integration test backup")

    # Upload directly to LocalStack.
    s3_client.upload_file(
        str(backup_file),
        backup.S3_BUCKET_NAME,
        backup_file.name,
    )

    # Verify the object exists.
    response = s3_client.head_object(
        Bucket=backup.S3_BUCKET_NAME,
        Key=backup_file.name,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
