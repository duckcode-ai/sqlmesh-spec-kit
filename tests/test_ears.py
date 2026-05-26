"""Tests for EARS pattern classification."""
from __future__ import annotations

import pytest

from sqlmesh_specify.ears import classify_ears


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("The system shall ship a CLI.", "ubiquitous"),
        ("the system must support snowflake", "ubiquitous"),
        ("When init is invoked, the system shall create .sqlmesh-specify/.", "event_driven"),
        ("While in plan mode, the system shall not write code.", "state_driven"),
        ("If no config.yaml exists, then the system shall exit non-zero.", "unwanted"),
        ("Where Snowflake is selected, the system shall add clustering hints.", "optional"),
    ],
)
def test_classify_ears_positive(line: str, expected: str) -> None:
    assert classify_ears(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "Hello world",
        "We should probably build a CLI",
        "Init creates .sqlmesh-specify/",
        "The system would maybe support snowflake",
    ],
)
def test_classify_ears_negative(line: str) -> None:
    assert classify_ears(line) is None
