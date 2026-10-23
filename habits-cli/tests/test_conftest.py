"""Smoke tests for the shared fixtures in conftest.py (TA-02)."""

from datetime import date
from pathlib import Path

import pytest


def test_today_is_fixed_date(today: date) -> None:
    assert today == date(2026, 10, 23)


def test_data_file_lives_in_fake_home_without_data_dir(
    tmp_path: Path, data_file: Path
) -> None:
    home = tmp_path / "home"
    assert data_file == home / ".habits" / "habits.json"
    assert home.is_dir()
    assert not data_file.parent.exists()


def test_write_raw_creates_data_dir_and_writes_exact_bytes(
    data_file: Path, write_raw
) -> None:
    content = b'{"version": 1}\x00\xff'
    write_raw(content)
    assert data_file.read_bytes() == content


def test_write_raw_accepts_empty_content(data_file: Path, write_raw) -> None:
    write_raw(b"")
    assert data_file.exists()
    assert data_file.read_bytes() == b""


def test_rf_7_5_assert_unchanged_passes_when_file_untouched(
    data_file: Path, write_raw, assert_unchanged
) -> None:
    write_raw(b"original")
    with assert_unchanged():
        data_file.read_bytes()


def test_rf_7_5_assert_unchanged_passes_when_file_stays_absent(
    data_file: Path, assert_unchanged
) -> None:
    with assert_unchanged():
        pass
    assert not data_file.exists()


def test_rf_7_5_assert_unchanged_fails_when_file_modified(
    data_file: Path, write_raw, assert_unchanged
) -> None:
    write_raw(b"original")
    with pytest.raises(AssertionError):
        with assert_unchanged():
            data_file.write_bytes(b"modified")


def test_rf_7_5_assert_unchanged_fails_when_file_created(
    write_raw, assert_unchanged
) -> None:
    with pytest.raises(AssertionError):
        with assert_unchanged():
            write_raw(b"new")


def test_rf_7_5_assert_unchanged_fails_when_file_deleted(
    data_file: Path, write_raw, assert_unchanged
) -> None:
    write_raw(b"original")
    with pytest.raises(AssertionError):
        with assert_unchanged():
            data_file.unlink()
