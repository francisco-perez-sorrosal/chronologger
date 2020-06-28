from .model import TimeEvent
from .repository import get_repo
from .timer import TimeContext


def register(timer: TimeContext):
    repo = get_repo()
    repo.register(timer)


def record(time_event: TimeEvent, parent_chrono: TimeContext = None):
    """Records every time event happening in the system"""
    repo = get_repo()
    repo.add(time_event, parent_chrono)


def show_time():
    """It's show time!!!"""
    print(get_repo())
