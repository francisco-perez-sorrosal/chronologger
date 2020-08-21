from .model import TimeEvent, Label
from .repository import get_repo
from .timer import TimeContext


def register(timer: TimeContext):
    get_repo().register(timer)


def label(name: str):
    time_event = Label(name, None)
    record(time_event)


def record(time_event: TimeEvent):
    """Records every time event happening in the system"""
    get_repo().add(time_event)


def show_time():
    """It's show time!!!"""
    print(get_repo())
