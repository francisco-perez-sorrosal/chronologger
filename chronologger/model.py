import time
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeEvent:
    name: str
    tick_secs: float = time.perf_counter()
