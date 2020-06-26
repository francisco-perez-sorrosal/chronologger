from .model import ChronologgerError, TimeEvent
from .repository import get_repo
from .timer import TimeContext


def register(timer: TimeContext):
    repo = get_repo()
    repo.register(timer)


def record(time_event: TimeEvent, parent_chrono: TimeContext = None):
    """Records every time event happening in the system"""
    repo = get_repo()
    if repo.get(time_event.name):
        raise ChronologgerError(f"An event with this name already exists in the repo:\n\t{time_event.name}")
    repo.add(time_event, parent_chrono)


def show_time():
    """It's show time!!!"""
    print(get_repo())
