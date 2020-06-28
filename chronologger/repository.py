import abc
from typing import Optional, List, Dict

from .model import TimeEvent, TimeContext


class AbstractTimeRepository(abc.ABC):
    name: str

    def register(self, time_context: TimeContext):
        raise NotImplementedError

    def add(self, time_event: TimeEvent):
        raise NotImplementedError

    def get(self, event_name) -> Optional[TimeEvent]:
        raise NotImplementedError

    def __str__(self):
        return f"Repo name: {self.name}"


class TimeRepository(AbstractTimeRepository):
    def __init__(self, root_time_context: TimeContext):
        self.name = root_time_context.name
        self.root_time_context = root_time_context
        self.time_events: List[TimeEvent] = []
        self.time_contexts: Dict[str, TimeContext] = {}
        self.register(self.root_time_context)
        self.root_time_context.chrono.logger(f"Repository {self.name} created")

    def register(self, time_context: TimeContext):
        if not self.time_contexts.get(time_context.name, None):
            self.time_contexts[time_context.name] = time_context
            self.root_time_context.chrono.logger(f"Timer {time_context.name} registered in repo {self.name}")

    def add(self, time_event: TimeEvent):
        self.time_events.append(time_event)

    def get(self, time_context: TimeContext) -> List[TimeEvent]:
        return self.time_contexts.get(time_context.name).get_all()

    def get_all(self) -> List[TimeEvent]:
        return self.time_events

    def __str__(self):
        representation = ""
        for time_event in self.time_events:  # TODO Skip printing single tick events (e.g. create an enum to differentiate TimeEvent types)
            representation += str(time_event) + "\n"
        return representation


class RootTimeRepository(TimeRepository):

    def __init__(self, root_context: TimeContext):
        TimeRepository.__init__(self, root_context)


time_repo: Optional[TimeRepository] = None


def init_repo(time_context: TimeContext = None):
    """
    Initializes the root time_repo.
    """

    global time_repo
    if not time_repo:
        time_context.chrono.logger(f"Creating root repo {time_context.name}")
        time_repo = RootTimeRepository(time_context)
    return time_repo


def get_repo() -> Optional[TimeRepository]:
    """
    Returns the root time_repo.
    """
    return time_repo
