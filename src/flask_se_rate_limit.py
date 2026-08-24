# SPDX-License-Identifier: Apache-2.0

import time
from collections import defaultdict

_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def is_rate_limited(ip: str, limit: int, window: int) -> bool:
    now = time.monotonic()
    window_start = now - window
    timestamps = _rate_limit_store[ip]
    timestamps[:] = [t for t in timestamps if t > window_start]
    if len(timestamps) >= limit:
        return True
    timestamps.append(now)
    return False