"""Shared fixtures: fixed date and an isolated data file (plan, section 8.2)."""

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import date
from pathlib import Path

import pytest

FIXED_TODAY = date(2026, 10, 23)


@pytest.fixture
def today() -> date:
    """Fixed "today" so no test depends on the real clock (RNF-5)."""
    return FIXED_TODAY


@pytest.fixture
def data_file(tmp_path: Path) -> Path:
    """Data file inside a fake home; the home exists, .habits does not yet."""
    home = tmp_path / "home"
    home.mkdir()
    return home / ".habits" / "habits.json"


@pytest.fixture
def write_raw(data_file: Path) -> Callable[[bytes], None]:
    """Write arbitrary bytes to the data file, creating .habits if needed."""

    def write(content: bytes) -> None:
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_bytes(content)

    return write


def _snapshot(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


@pytest.fixture
def assert_unchanged(
    data_file: Path,
) -> Callable[[], AbstractContextManager[None]]:
    """Context manager that fails if the data file changes inside it (RF-7.5).

    Compares the exact bytes, and also detects the file being created or
    deleted.
    """

    @contextmanager
    def check() -> Iterator[None]:
        before = _snapshot(data_file)
        yield
        after = _snapshot(data_file)
        assert after == before, "the data file was modified"

    return check
