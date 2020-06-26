from typing import List

from chronologger.model import Tick, TimeEvent
from chronologger.repository import AbstractTimeRepository
from chronologger.service import record

time_event_name = "tick"

#
# class FlatTimeRepository(AbstractTimeRepository):
#     time_events: List[TimeEvent] = list()
#
#     def __init__(self, name):
#         self.name = name
#
#     def add(self, time_event: TimeEvent):
#         self.time_event.append(time_event)
#
#     def get(self):
#         self.time_events[-1]
#
#     def add(self, TimeUnit):
#         pass


def test_events_recording():
    tick = Tick(time_event_name)
    last_recorded_time_event = record(tick)
    assert last_recorded_time_event == tick
