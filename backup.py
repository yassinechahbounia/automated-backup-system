#!/usr/bin/env python3

"""
Automated Backup System

Creates compressed TAR.GZ backups of the data directory,
removes old backups according to a retention policy,
and records execution details in a log file.
"""

import logging
import tarfile

from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

# Directory containing the files that must be backed up.
SOURCE_DIR = Path("data")

# Directory where backup archives will be stored.
BACKUP_DIR = Path("backups")

# Directory containing application logs.
LOG_DIR = Path("logs")

# Log file.
LOG_FILE = LOG_DIR / "backup.log"

# Number of days backups should be kept.
RETENTION_DAYS = 7


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
    """
    Main application entry point.
    """

    setup_logging()

    logging.info(
        "========================================"
    )

    logging.info(
        "Automated Backup System started"
    )

    logging.info(
        "========================================"
    )

    try:

        # Create backup.
        create_backup()

        # Remove old backups.
        delete_old_backups()

        logging.info(
            "Backup process completed successfully."
        )

    except Exception:

        # logging.exception() automatically includes
        # the error message and traceback.

        logging.exception(
            "Backup process failed."
        )

        # Return a non-zero exit code.
        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()