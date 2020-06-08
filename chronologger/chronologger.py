import enum
import itertools
import time
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Set, ClassVar, Tuple, List


class ChronologgerError(Exception):
    """A general exception used to report errors in use of the Chronologger project"""


class TimeUnit(enum.Enum):
    ns = (9)
    ms = (3)
    s = (0)

    def __init__(self, x) -> None:
        self.x = x

    def from_secs(self, secs: float) -> float:
        return secs * 10 ** self.x

    def to_secs(self, timelapse: float) -> float:
        return timelapse / 10 ** self.x

    def from_secs_as_str(self, secs: float) -> str:
        format_str = "{:0.3f} {}" if self.name == "s" else "{:0.0f} {}"
        return format_str.format(self.from_secs(secs), self.name)


@dataclass
class Chronologger(ContextDecorator):
    """A basic timer utility for logging time in code. It can be used as a class, context manager or decorator"""

    id_iter: ClassVar[int] = itertools.count()

    unique_names: ClassVar[Set[str]] = set()

    name: str = None
    description: str = ""
    hierarchy_level: int = 0
    unit: TimeUnit = TimeUnit.s
    text: str = "{} elapsed"
    logger: Optional[Callable[[str], None]] = print
    simple_log_msgs: bool = True
    log_when_exiting_context: bool = False
    markers: List[Tuple[str, float]] = field(default_factory=list)
    _start_time_in_secs: Optional[float] = field(default=None, init=False, repr=False)
    _last_time_in_secs: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization: add unique name at least"""
        if not self.name:
            self.name = "timer_" + str(next(Chronologger.id_iter))
        if self.name in Chronologger.unique_names:
            raise ChronologgerError("{} timer name already exists! Use a "
                                    "unique identifier for your timer".format(self.name))
        Chronologger.unique_names.add(self.name)

    def start(self, initial_gap_name: str = "initial_gap") -> "Chronologger":
        """Start a new basic timer"""
        if self._start_time_in_secs is not None:
            raise ChronologgerError(
                f"Timer is already running. Use .reset() or .stop(reset=True) to reuse this timer again safely")

        self._start_time_in_secs = time.perf_counter()
        self._mark(initial_gap_name, secs=self._start_time_in_secs)

        return self

    def stop(self, do_log: bool = False, reset: bool = False) -> Tuple[Optional[float], float]:
        """Stop the basic timer reporting the elapsed time"""
        if self._start_time_in_secs is None:
            raise ChronologgerError(f"Timer not started yet. Use .start() to start counting time...")

        # Calculate elapsed time
        self._last_time_in_secs = stop_time_in_secs = time.perf_counter()
        elapsed_time_in_secs = self._last_time_in_secs - self._start_time_in_secs

        # Report elapsed time
        if self.logger and do_log:
            self.logger(self.text.format(self.unit.from_secs_as_str(elapsed_time_in_secs))
                        if self.simple_log_msgs else self.logger(self))

        self.reset() if reset else None

        return stop_time_in_secs, self.unit.from_secs(elapsed_time_in_secs)

    def _mark(self, name: str, secs: float = None) -> None:
        self.markers.append((name, self.stop()[0] if not secs else secs))

    def mark(self, name: str) -> None:
        self._mark(name)

    def reset(self) -> None:
        self._start_time_in_secs = self._last_time_in_secs = None
        self.markers = []

    def __enter__(self) -> "Chronologger":
        """Start a new basic timer as a context manager"""
        self.start() if not self._start_time_in_secs else None
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Stop the basic timer when exiting the context"""
        self.stop(do_log=self.log_when_exiting_context)

    def __repr__(self) -> str:
        markers_str = ""
        if self.markers and self._last_time_in_secs:
            previous_maker = self.markers[0]
            i = 1
            while i <= len(self.markers):
                marker = self.markers[i] if i != len(self.markers) else ('last_gap', self._last_time_in_secs)
                markers_str += "\t{}. {} elapsed -> {}\t= {} - {}\n\t".format(i,
                                                                              previous_maker[0],
                                                                              self.unit.from_secs_as_str(
                                                                                  marker[1] - previous_maker[1]),
                                                                              self.unit.from_secs_as_str(marker[1]),
                                                                              self.unit.from_secs_as_str(
                                                                                  previous_maker[1]))
                previous_maker = marker
                i += 1

        return """"
        --------------------------------------------------------------------------------
        {} ({}) Elapsed time {}\t= {} - {}
        {}
        --------------------------------------------------------------------------------
        Marks:
        {}
        --------------------------------------------------------------------------------
        """.format(self.name,
                   self.hierarchy_level,
                   self.unit.from_secs_as_str(self._last_time_in_secs - self._start_time_in_secs)
                                  if self._start_time_in_secs and self._last_time_in_secs else 0.0,
                   self.unit.from_secs_as_str(self._last_time_in_secs) if self._last_time_in_secs else 0.0,
                   self.unit.from_secs_as_str(self._start_time_in_secs) if self._start_time_in_secs else 0.0,
                   self.description,
                   markers_str,
                   )
