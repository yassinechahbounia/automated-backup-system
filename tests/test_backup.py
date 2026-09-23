import tarfile

from pathlib import Path

import backup


def test_create_backup(tmp_path, monkeypatch):
    """
    Test that a backup archive is correctly created.
    """

    # Create a temporary source directory.
    source_dir = tmp_path / "data"

    source_dir.mkdir()

    # Create a test file.
    test_file = source_dir / "test.txt"

    test_file.write_text(
        "Hello Backup"
    )

    # Create a temporary backup directory.
    backup_dir = tmp_path / "backups"

    # Replace the real application directories
    # with temporary directories.

    monkeypatch.setattr(
        backup,
        "SOURCE_DIR",
        source_dir
    )

    monkeypatch.setattr(
        backup,
        "BACKUP_DIR",
        backup_dir
    )

    # Execute the backup.
    backup_path = backup.create_backup()

    # Verify that the archive exists.
    assert backup_path.exists()

    # Verify that it is a TAR.GZ file.
    assert tarfile.is_tarfile(
        backup_path
    )


def test_delete_old_backups(
    tmp_path,
    monkeypatch
):
    """
    Test that the backup directory is handled correctly.
    """

    backup_dir = tmp_path / "backups"

    backup_dir.mkdir()

    monkeypatch.setattr(
        backup,
        "BACKUP_DIR",
        backup_dir
    )

    # Create a recent backup.
    recent_backup = (
        backup_dir
        / "backup_recent.tar.gz"
    )

    recent_backup.write_text(
        "test"
    )

    # Run cleanup.
    backup.delete_old_backups()

    # Recent backup should still exist.
    assert recent_backup.exists()
