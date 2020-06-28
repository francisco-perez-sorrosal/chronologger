from typing import Any, cast

from chronologger.model import Period, TimeContext, TimeEvent, Chronologger, TimeUnit
from chronologger.service import record, register, show_time


class Timer(TimeContext):
    """A basic timer utility for logging time in code. It can be used as a class, context manager or decorator"""

    def __init__(self, name, unit=TimeUnit.s, simple_log=False, log_when_exiting=False, parent_ctx=None):
        self.name = name
        self.chrono = Chronologger(name, self, unit, simple_log_msgs=simple_log)
        self.log_when_exiting = log_when_exiting
        self.parent_ctx: TimeContext = parent_ctx
        self.chrono.logger(f"{self.name} Timer created!")

    def start(self, start_suffix: str = "_start_tick") -> "Timer":
        time_event: TimeEvent = self.chrono.start(self.name + start_suffix)
        record(time_event)
        return self

    def mark(self, name: str) -> "TimeEvent":
        # register(self)
        time_event: TimeEvent = self.chrono.mark(name)
        record(time_event)
        return time_event

    def stop(self, end_suffix: str = "_end_tick", do_log: bool = False, reset: bool = False) -> Period:
        time_event: Period = self.chrono.stop(self.name + end_suffix, do_log, reset)
        record(cast(TimeEvent, time_event))
        return time_event

    def print(self):
        show_time()

    """ContextDecorator implementation"""

    def __enter__(self) -> "Timer":
        """Start a new basic timer as a context manager"""
        register(self)
        self.start("_start_tick")
        return self

    """Presentation dunder implementations"""

    def __exit__(self, *exc_info: Any) -> None:
        """Stop the basic timer when exiting the context"""
        self.stop("_end_tick", do_log=self.log_when_exiting,
                  reset=True)  # TODO Make this last param configurable

    def __str__(self) -> str:
        if self.chrono.ticks.last() is None:
            tick_diff = ""
        else:
            tick_diff = (self.chrono.ticks.last() - self.chrono.ticks.first())
        representation = (
            f"\n------------------------------------------------------------------------------------------\n"
            f"{self.chrono.name}\t{tick_diff}\n"
            f"{self.chrono.description}\n"
            f"Has parent context: {self.parent_ctx}\n"
            f"------------------------------------------------------------------------------------------\n"
        )
        if len(self.chrono.ticks) > 2:
            representation += (
                f"Marks:\n"
                f"{self.chrono.ticks}\n"
                f"------------------------------------------------------------------------------------------\n"
            )
        return representation
