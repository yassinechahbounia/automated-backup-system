#!/usr/bin/env python3

"""
Automated Backup System

Creates compressed TAR.GZ backups of the data directory,
removes old backups according to a retention policy,
and records execution details in a log file.
"""
import boto3
import os
import logging
import tarfile

from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError
# Load environment variables from .env file
load_dotenv()

# ===============================================================
# CONFIGURATION
# ============================================================

# Absolute path of the project directory.
# __file__ = location of backup.py
BASE_DIR = Path(__file__).resolve().parent

# Directory containing the files that must be backed up.
SOURCE_DIR = BASE_DIR / "data"

# Directory where backup archives will be stored.
BACKUP_DIR = BASE_DIR / "backups"

# Directory containing application logs.
LOG_DIR = BASE_DIR / "logs"

# Log file.
LOG_FILE = LOG_DIR / "backup.log"

# Number of days backups should be kept.
RETENTION_DAYS = 7

# LocalStack S3 configuration
# ============================================================
# S3 CONFIGURATION
# ============================================================

S3_ENDPOINT_URL = os.getenv(
    "S3_ENDPOINT_URL",
    "http://localhost:4566"
)

S3_BUCKET_NAME = os.getenv(
    "S3_BUCKET_NAME",
    "automated-backup-system"
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)

AWS_ACCESS_KEY_ID = os.getenv(
    "AWS_ACCESS_KEY_ID",
    "test"
)

AWS_SECRET_ACCESS_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY",
    "test"
)
# ============================================================
# LOGGING CONFIGURATION
# ============================================================

def setup_logging():
    """
    Configure the application logging system.

    Logs are written both:
    - to the terminal
    - to logs/backup.log
    """

    # Create the logs directory if necessary.
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Configure logging.
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
        handlers=[
            # Display logs in the terminal.
            logging.StreamHandler(),

            # Save logs to a file.
            logging.FileHandler(
                LOG_FILE
            ),
        ],
    )


# ============================================================
# CREATE BACKUP
# ============================================================

def create_backup():
    """
    Create a compressed TAR.GZ backup.

    Returns:
        Path: Path of the generated backup.
    """

    # Verify that the source directory exists.
    if not SOURCE_DIR.exists():

        raise FileNotFoundError(
            f"Source directory not found: {SOURCE_DIR}"
        )

    # Create backup directory if necessary.
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generate timestamp.

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    # Generate backup filename.

    backup_filename = (
        f"backup_{timestamp}.tar.gz"
    )

    # Generate complete backup path.

    backup_path = (
        BACKUP_DIR / backup_filename
    )

    logging.info(
        "Starting backup..."
    )

    logging.info(
        "Source directory: %s",
        SOURCE_DIR
    )

    logging.info(
        "Backup destination: %s",
        backup_path
    )

    # Create TAR.GZ archive.

    with tarfile.open(
        backup_path,
        "w:gz"
    ) as tar:

        tar.add(
            SOURCE_DIR,
            arcname="data"
        )

    logging.info(
        "Backup created successfully: %s",
        backup_path
    )

    return backup_path

def upload_to_s3(backup_path):
    """
    Upload the backup archive to the configured S3 bucket.
    """

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        logging.info(
            "Uploading backup to S3: %s",
            backup_path.name,
        )

        s3.upload_file(
            str(backup_path),
            S3_BUCKET_NAME,
            backup_path.name,
        )

        logging.info(
            "Backup uploaded successfully to S3 bucket '%s'",
            S3_BUCKET_NAME,
        )

    except (BotoCoreError, ClientError):
        logging.exception(
            "Failed to upload backup to S3"
        )
        raise
# ============================================================
# DELETE OLD BACKUPS
# ============================================================

def delete_old_backups():
    """
    Delete backups older than RETENTION_DAYS.
    """

    # Calculate retention limit.

    limit_date = (
        datetime.now()
        - timedelta(
            days=RETENTION_DAYS
        )
    )

    logging.info(
        "Checking old backups..."
    )

    # Find backup archives.

    for backup_file in BACKUP_DIR.glob(
        "backup_*.tar.gz"
    ):

        # Get modification time.

        modification_time = (
            datetime.fromtimestamp(
                backup_file.stat().st_mtime
            )
        )

        # Delete old backup.

        if modification_time < limit_date:

            logging.info(
                "Deleting old backup: %s",
                backup_file
            )

            backup_file.unlink()


# ============================================================
# MAIN
# ============================================================

def main():
    setup_logging()

    try:
        logging.info("Starting backup process")

        backup_path = create_backup()

        upload_to_s3(backup_path)

        delete_old_backups()

        logging.info("Backup process completed successfully")

    except Exception:
        logging.exception("Backup process failed")
        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()