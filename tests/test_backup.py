import sys
import os
import tarfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import backup

def test_create_backup(tmp_path, monkeypatch):
    """
    Test that a backup archive is created correctly.
    """

    # Create temporary source directory.
    source_dir = tmp_path / "data"
    source_dir.mkdir()

    # Create a test file.
    test_file = source_dir / "test.txt"
    test_file.write_text("Hello Backup")

    # Create temporary backup directory.
    backup_dir = tmp_path / "backups"

    # Replace application directories with temporary ones.
    monkeypatch.setattr(backup, "SOURCE_DIR", source_dir)
    monkeypatch.setattr(backup, "BACKUP_DIR", backup_dir)

    # Create backup.
    backup_path = backup.create_backup()

    # Verify backup exists.
    assert backup_path.exists()

    # Verify it is a valid tar archive.
    assert tarfile.is_tarfile(backup_path)

    # Verify the test file is inside the archive.
    with tarfile.open(backup_path, "r:gz") as archive:
        files = archive.getnames()

    assert "data/test.txt" in files


def test_delete_old_backups(tmp_path, monkeypatch):
    """
    Test that backups older than the retention period are deleted.
    """

    # Create temporary backup directory.
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    monkeypatch.setattr(backup, "BACKUP_DIR", backup_dir)

    # Create an old backup.
    old_backup = backup_dir / "backup_old.tar.gz"
    old_backup.write_text("old backup")

    # Create a recent backup.
    recent_backup = backup_dir / "backup_recent.tar.gz"
    recent_backup.write_text("recent backup")

    # Make old backup older than retention period.
    old_timestamp = (
        datetime.now()
        - timedelta(days=backup.RETENTION_DAYS + 1)
    ).timestamp()

    os.utime(old_backup, (old_timestamp, old_timestamp))

    # Run retention cleanup.
    backup.delete_old_backups()

    # Old backup should be deleted.
    assert not old_backup.exists()

    # Recent backup should remain.
    assert recent_backup.exists()

def test_upload_to_s3(tmp_path, monkeypatch):
    """
    Test that a backup file is uploaded to S3 correctly.
    """

    # Create a fake backup file.
    backup_file = tmp_path / "backup_test.tar.gz"
    backup_file.write_text("fake backup")

    # Create a mock S3 client.
    mock_s3 = MagicMock()

    # Replace boto3.client with a mock.
    monkeypatch.setattr(
        backup.boto3,
        "client",
        lambda *args, **kwargs: mock_s3,
    )

    # Run the upload function.
    backup.upload_to_s3(backup_file)

    # Verify upload_file was called correctly.
    mock_s3.upload_file.assert_called_once_with(
        str(backup_file),
        backup.S3_BUCKET_NAME,
        backup_file.name,
    )