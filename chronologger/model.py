import enum
import itertools
import time
from abc import abstractmethod, ABC
from contextlib import ContextDecorator
from dataclasses import dataclass, field, replace
from typing import List, Optional, ClassVar, Callable, Any

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


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


@runtime_checkable
class TimeEvent(Protocol):
    """Main concept of the library, representing a discrete time event"""
    name: str
    unit: TimeUnit

    @abstractmethod
    def time(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def to(self, unit: TimeUnit) -> 'TimeEvent':
        raise NotImplementedError

    @abstractmethod
    def __sub__(self, other: 'TimeEvent') -> 'Period':
        raise NotImplementedError


@dataclass(frozen=True)
class Tick:
    """A discrete time event implementation"""
    name: str
    unit: TimeUnit = TimeUnit.s
    # I decided to store the time in secs but this is just an implementation detail
    _tick_in_secs: float = field(default_factory=lambda: time.perf_counter(), init=False, repr=False)

    def time(self) -> float:
        """Returns the value of the time in the TimeUnits in which the object is specified"""
        return self.unit.from_secs(self._tick_in_secs)

    def to(self, unit: TimeUnit) -> 'Tick':
        if unit == self.unit:
            return self
        else:  # Create new object with a new time unit. Immutability broken, but just in the creation of a new object
            new_object = replace(self, unit=unit)
            object.__setattr__(new_object, '_tick_in_secs', self._tick_in_secs)
            return new_object

    def __sub__(self, other: TimeEvent) -> 'Period':
        if other is None:
            return self
        return Period("elapsed", other.unit, other, self)

    def __str__(self) -> str:
        return f"{self.name}: {self.time():.3f} {self.unit.name}"


@dataclass(frozen=True)
class Period:
    """Represents the elapsed time between two time events.

    We allow heterogeneous Periods when explicitly created, meaning
    that the ticks passed can have different TimeUnits. Calculations to
    reconcile the results are done when results are presented."
    """
    name: str
    unit: TimeUnit
    start: TimeEvent
    end: TimeEvent

    # If we don't want to allow heterogeneus Periods (see class description) uncomment
    # this and change the semantics
    # def __post_init__(self):
    #     if self.start.unit != self.unit or self.end.unit != self.unit:
    #         message = (
    #             f"Ether start or end ticks have different units from Period units."
    #             f"start tick {self.start.name} -> {self.start.unit.name}"
    #             f"end tick {self.end.name} -> {self.end.unit.name}"
    #             f"Please convert them first"
    #         )
    #         raise ChronologgerError(message)

    def elapsed(self) -> float:
        """Returns the value of the elapsed time in the TimeUnits in which the object is specified"""
        start_in_current_units = self.start.to(self.unit).time()
        end_in_current_units = self.end.to(self.unit).time()
        return end_in_current_units - start_in_current_units

    def time(self) -> float:
        """Returns the value of the elapsed time in the TimeUnits in which the object is specified"""
        return self.elapsed()

    def to(self, unit: TimeUnit) -> 'Period':
        return Period(self.name, unit, self.start, self.end)

    def __sub__(self, other: 'Period') -> 'Period':
        """Builds a new Period from the parts of the two periods involved.

        Instead of keeping a Frankenstein period, we get the start tick from
        the subtracting period and the end tick from the minuend. The time
        unit from the new period will be the one from the start_tick."""
        new_time_unit = other.unit
        new_start_tick = other.start.to(new_time_unit)
        new_end_tick = self.end.to(new_time_unit)
        return Period(f"elapsed ({new_end_tick.name} - {new_start_tick.name})",
                      new_time_unit, new_start_tick, new_end_tick)

    def __str__(self) -> str:
        return f"{self.time():.3f} {self.unit.name} ({self.name})   =    {self.end} - {self.start}"


@dataclass(frozen=True)
class EventRecorder:
    """Stores a list of time events"""
    events: List[TimeEvent] = field(default_factory=list)

    def add(self, event: TimeEvent) -> Optional[Period]:
        """Add a new time event to the recorded list

        Parameters
        ----------
        event : The time event to store

        Returns
        -------
        the (optional) period (TimeEvent) from the initial time event recorded
        """
        self.events.append(event)
        return self.elapsed()

    def first(self) -> Optional[TimeEvent]:
        return None if len(self.events) == 0 else self.events[0]

    def last(self) -> Optional[TimeEvent]:
        return None if len(self.events) == 0 else self.events[-1]

    def elapsed(self) -> Optional[Period]:
        return None if len(self.events) == 0 else self.last() - self.first()

    def get_all(self) -> List[TimeEvent]:
        return self.events

    def to(self, unit: TimeUnit):
        converted_event_recorder = EventRecorder()
        for event in self.events:
            converted_event_recorder.add(event.to(unit))
        return converted_event_recorder

    def __len__(self) -> int:
        return len(self.events)

    def __str__(self) -> str:
        if len(self.events) == 0:
            return ""
        previous_marker = self.events[0]
        time_unit = previous_marker.unit  # Reporting in the time unit of the first TimeEvent
        markers_str = ""
        i = 1
        while i < len(self.events):
            marker = self.events[i]
            period = Period(marker.name, time_unit, previous_marker, marker)
            markers_str += f"\t- {period}\n"
            previous_marker = marker
            i += 1
        return markers_str


def event_recorder():
    return EventRecorder()


@dataclass(frozen=False)
class Chronologger:
    """Core class. Manages the creation of every tick and period."""

    id_iter: ClassVar[int] = itertools.count()

    name: Optional[str] = None
    unit: TimeUnit = TimeUnit.s
    description: str = ""
    hierarchy_level: int = 0
    logger: Callable[[str], None] = print
    simple_log_msgs: bool = True
    ticks: EventRecorder = field(default_factory=event_recorder)

    parent: Optional[str] = None

    def __post_init__(self) -> None:  # TODO This is not necessary anymore... but leave it for now...
        """Initialization: add unique name at least"""
        if not self.name:
            object.__setattr__(self, 'name', "timer_" + str(next(Chronologger.id_iter)))

    def start(self, start_tick_name: str = "start_tick") -> TimeEvent:
        """Start a new basic timer"""
        time_event = Tick(start_tick_name, self.unit)
        self.ticks.add(time_event)
        return time_event

    def _report_time(self, do_log, period):
        if self.logger and do_log:
            self.logger(f"{period.time():3f} {period.unit.name} elapsed time") if self.simple_log_msgs else self.logger(
                self)

    def stop(self, final_tick_name: str = "end_tick", do_log: bool = False, reset: bool = False) -> Period:
        """Stop the basic timer reporting the elapsed time"""
        if len(self.ticks) == 0:
            raise ChronologgerError(f"Timer not started yet! Use .start() to start counting time...")

        tick = Tick(final_tick_name, unit=self.unit)

        period: Period = self.ticks.add(tick)
        self._report_time(do_log, period)

        self.reset() if reset else None

        return period.to(self.unit)

    def mark(self, name: str) -> TimeEvent:
        tick = Tick(name, unit=self.unit)
        self.ticks.add(tick)
        return tick

    def reset(self) -> None:
        self.ticks = EventRecorder()

    def get_all(self) -> List[TimeEvent]:
        return self.ticks.get_all()


class TimeContext(ContextDecorator, ABC):
    name: str
    parent_ctx: "TimeContext"
    decorated: bool
    chrono: Chronologger = field(default_factory=Chronologger)
    log_when_exiting: bool = False

    # TODO Create method to allow to report phases e.g. def phase():

    def get_all(self):
        return self.chrono.get_all()

    @abstractmethod
    def __enter__(self) -> "TimeContext":
        pass

    @abstractmethod
    def __exit__(self, *exc_info: Any):
        pass
