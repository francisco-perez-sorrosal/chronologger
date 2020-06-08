import time

from chronologger.model import TimeEvent


def test_time_event():
    te = TimeEvent("tick")
    now = time.perf_counter_ns()
    assert te.tick_secs < now
    time.sleep(0.05)
    te1 = TimeEvent("tock")
    assert te.tick_secs < te1.tick_secs

    assert not te == te1

    time.sleep(1)
    te2 = TimeEvent("tock")

    assert not te1 == te2