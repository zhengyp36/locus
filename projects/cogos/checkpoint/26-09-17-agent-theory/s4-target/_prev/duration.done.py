"""Duration parsing helper (S4 minimal criterion target)."""

import re

_UNIT_SECONDS = {"h": 3600, "m": 60, "s": 1}
_SEGMENT_RE = re.compile(r"(\d+)([hms])")


def parse_duration(text: str) -> int:
    """Parse a compact duration like '1h30m' or '45s' into total seconds.

    The input is a sequence of ``<number><unit>`` segments where the unit is
    one of ``h`` (hours), ``m`` (minutes) or ``s`` (seconds). Segments are
    summed into a total number of seconds. A ``ValueError`` is raised for any
    malformed input.
    """
    if not isinstance(text, str) or not text:
        raise ValueError(f"invalid duration: {text!r}")

    total = 0
    pos = 0
    for match in _SEGMENT_RE.finditer(text):
        if match.start() != pos:
            raise ValueError(f"invalid duration: {text!r}")
        value = int(match.group(1))
        total += value * _UNIT_SECONDS[match.group(2)]
        pos = match.end()

    if pos != len(text):
        raise ValueError(f"invalid duration: {text!r}")

    return total
