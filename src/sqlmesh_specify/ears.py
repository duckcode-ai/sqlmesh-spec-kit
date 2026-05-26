"""EARS pattern classification.

EARS = Easy Approach to Requirements Syntax. Five patterns:

  1. Ubiquitous:    "The system shall <response>."
  2. Event-driven:  "When <trigger>, the system shall <response>."
  3. State-driven:  "While <state>, the system shall <response>."
  4. Unwanted:      "If <unwanted>, then the system shall <response>."
  5. Optional:      "Where <feature>, the system shall <response>."

We use loose matching — the requirement phrasing must contain the right
trigger keyword *and* the "shall" verb. Punctuation and capitalization
are tolerant.
"""
from __future__ import annotations

import re

# All patterns require " shall " or " must " somewhere after the trigger.
_RESPONSE_VERB = r"(shall|must)"


# Order matters: more specific (Event/State/Unwanted/Optional) before Ubiquitous.
_PATTERNS = [
    (
        "event_driven",
        re.compile(
            rf"^\s*when\b.*?,?\s*the\s+system\s+{_RESPONSE_VERB}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "state_driven",
        re.compile(
            rf"^\s*while\b.*?,?\s*the\s+system\s+{_RESPONSE_VERB}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "unwanted",
        re.compile(
            rf"^\s*if\b.*?,?\s*then\s+the\s+system\s+{_RESPONSE_VERB}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "optional",
        re.compile(
            rf"^\s*where\b.*?,?\s*the\s+system\s+{_RESPONSE_VERB}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "ubiquitous",
        re.compile(
            rf"^\s*the\s+system\s+{_RESPONSE_VERB}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
]


def classify_ears(line: str) -> str | None:
    """Return the EARS pattern name for a given line, or None if not EARS.

    Recognised pattern names: "ubiquitous", "event_driven", "state_driven",
    "unwanted", "optional".
    """
    for name, pattern in _PATTERNS:
        if pattern.search(line):
            return name
    return None
