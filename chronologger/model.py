import enum
import time
from abc import abstractmethod
from dataclasses import dataclass, field, replace
from typing import List, Optional

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
        return Period("elapsed", unit, self.start, self.end)

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
        return f"{self.name}: {self.time():.3f} {self.unit.name}    =    {self.end} - {self.start}"


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
