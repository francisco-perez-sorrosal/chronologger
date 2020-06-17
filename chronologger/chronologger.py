import itertools
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from typing import Any, Callable, Set, ClassVar, Optional

from chronologger.model import Tick, TimeUnit, Period, ChronologgerError, EventRecorder


def event_recorder():
    return EventRecorder()


@dataclass(frozen=False)
class Chronologger(ContextDecorator):
    """A basic timer utility for logging time in code. It can be used as a class, context manager or decorator"""

    id_iter: ClassVar[int] = itertools.count()

    unique_names: ClassVar[Set[str]] = set()

    name: Optional[str] = None
    description: str = ""
    hierarchy_level: int = 0
    unit: TimeUnit = TimeUnit.s
    logger: Callable[[str], None] = print
    simple_log_msgs: bool = True
    log_when_exiting_context: bool = False
    ticks: EventRecorder = field(default_factory=event_recorder)

    def __post_init__(self) -> None:
        """Initialization: add unique name at least"""
        if not self.name:
            object.__setattr__(self, 'name', "timer_" + str(next(Chronologger.id_iter)))
        if self.name in Chronologger.unique_names:
            raise ChronologgerError("{} timer already exists! Use a unique name for your timer!".format(self.name))
        Chronologger.unique_names.add(self.name)
        self.logger(f"{self.name} created!")

    def start(self, initial_tick_name: str = "start_tick") -> "Chronologger":
        """Start a new basic timer"""
        if len(self.ticks) > 0:
            raise ChronologgerError("Timer is already running! .reset() or .stop(reset=True) to reuse this timer")

        self.ticks.add(Tick(initial_tick_name, unit=self.unit))

        return self

    def _report_time(self, do_log, period):
        if self.logger and do_log:
            self.logger(f"{period.time():3f} {period.unit.name} elapsed") if self.simple_log_msgs else self.logger(self)

    def stop(self, final_tick_name: str = "end_tick", do_log: bool = False, reset: bool = False) -> Period:
        """Stop the basic timer reporting the elapsed time"""
        if len(self.ticks) == 0:
            raise ChronologgerError(f"Timer not started yet! Use .start() to start counting time...")

        period: Period = self.ticks.add(Tick(final_tick_name, unit=self.unit))

        self._report_time(do_log, period)

        self.reset() if reset else None

        return period.to(self.unit)

    def mark(self, name: str) -> None:
        self.ticks.add(Tick(name, unit=self.unit))

    def reset(self) -> None:
        self.ticks = EventRecorder()

    def __enter__(self) -> "Chronologger":
        """Start a new basic timer as a context manager"""
        self.start() if len(self.ticks) == 0 else None
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Stop the basic timer when exiting the context"""
        self.stop(do_log=self.log_when_exiting_context)
        self.reset()  # TODO Make this configurable

    def __repr__(self) -> str:
        representation = (
            f"------------------------------------------------------------------------------------------\n"
            f"{self.name} ({self.hierarchy_level})\t{self.ticks.last() - self.ticks.first()}"
            f"{self.description}\n"
            f"------------------------------------------------------------------------------------------\n"
        )
        if len(self.ticks) > 2:
            representation += (
                f"Marks:\n"
                f"{self.ticks}\n"
                f"------------------------------------------------------------------------------------------\n"
            )
        return representation
