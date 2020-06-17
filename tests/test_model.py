import math
import time

from chronologger.model import Tick, TimeUnit, EventRecorder, TimeEvent, Period

time_event_name = "tick"


def test_tick_basic_properties():
    tick = Tick(time_event_name)
    assert tick.name == time_event_name
    assert tick.unit == TimeUnit.s
    now = time.perf_counter()
    assert tick.time() < now


def test_tick_representation(capsys):
    tick = Tick(time_event_name)
    print(tick)
    captured = capsys.readouterr()
    assert time_event_name in captured.out


def test_tick_conversions():
    tick = Tick(time_event_name)

    tick_in_secs_again = tick.to(TimeUnit.s)
    assert tick_in_secs_again == tick

    tick_ms = tick.to(TimeUnit.ms)
    assert tick_ms.name == tick.name
    assert tick_ms.unit == TimeUnit.ms
    assert math.isclose(tick_ms.time(), tick.time() * 10 ** tick_ms.unit.value, rel_tol=0.02)

    tick_ns = tick.to(TimeUnit.ns)
    assert tick_ns.name == tick.name
    assert tick_ns.unit == TimeUnit.ns
    assert math.isclose(tick_ns.time(), tick.time() * 10 ** tick_ns.unit.value, rel_tol=0.02)
    now_in_ns = time.perf_counter() * 10 ** 9
    assert tick_ns.time() < now_in_ns


def test_two_ticks_with_the_same_name_are_different_as_they_have_different_timestamps():
    tick_1 = Tick("tock")
    tick_2 = Tick("tock")
    assert not tick_1 == tick_2
    assert tick_1.time() < tick_2.time()


def test_basic_homogeneus_period():
    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick")
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tock")

    explicit_period = Period("test_period", TimeUnit.s, tick_1, tick_2)
    assert isinstance(explicit_period, TimeEvent)
    assert isinstance(explicit_period, Period)
    assert explicit_period.name == "test_period"
    assert explicit_period.unit == TimeUnit.s
    assert math.isclose(explicit_period.elapsed(), sleep_time_secs, rel_tol=0.05)

    calculated_period = tick_2 - tick_1
    assert isinstance(calculated_period, TimeEvent)
    assert isinstance(calculated_period, Period)
    assert calculated_period.name == "elapsed"  # This is the default name
    assert calculated_period.unit == TimeUnit.s
    assert math.isclose(calculated_period.elapsed(), sleep_time_secs, rel_tol=0.05)


def test_basic_heterogeneous_period(capsys):
    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick")
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tock", TimeUnit.ns)

    period_name = "test_period"
    explicit_period_ms = Period(period_name, TimeUnit.ms, tick_1, tick_2)
    tick_1_ms = tick_1.to(TimeUnit.ms).time()
    tick_2_ms = tick_2.to(TimeUnit.ms).time()
    print(tick_1_ms)
    print(tick_2_ms)
    print(explicit_period_ms.elapsed())
    assert math.isclose(explicit_period_ms.elapsed(), tick_2_ms - tick_1_ms, abs_tol=0.05)
    print(explicit_period_ms)
    captured = capsys.readouterr()
    assert period_name in captured.out
    assert TimeUnit.ms.name in captured.out


def test_heterogeneous_period_gets_converted_properly_to_homogeneous(capsys):
    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick")
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tock", TimeUnit.ns)

    heterogeneous_period = tick_2 - tick_1
    homogeneous_period: Period = heterogeneous_period.to(TimeUnit.ms)
    assert homogeneous_period.name == "elapsed"
    assert homogeneous_period.start == tick_1
    assert homogeneous_period.end == tick_2
    assert homogeneous_period.start.unit == TimeUnit.s
    assert homogeneous_period.end.unit == TimeUnit.ns
    assert math.isclose(homogeneous_period.elapsed(),
                        homogeneous_period.end.to(TimeUnit.ms).time() - homogeneous_period.start.to(TimeUnit.ms).time(),
                        abs_tol=0.05)

    print(homogeneous_period)
    captured = capsys.readouterr()
    assert "elapsed" in captured.out
    assert TimeUnit.ms.name in captured.out


def test_event_recorder_can_hold_and_retrieve_events():
    num_of_time_events_to_create = 3
    event_recorder = EventRecorder()
    for i in range(0, num_of_time_events_to_create):
        event_recorder.add(Tick(f"evt {i}"))
        time.sleep(0.1)
    assert len(event_recorder.get_all()) == num_of_time_events_to_create


def test_event_recorder_can_homogeinize_different_event_time_units():
    event_recorder = EventRecorder()
    tick_1 = Tick(f"evt 1", unit=TimeUnit.s)
    event_recorder.add(tick_1)
    time.sleep(0.1)
    tick_2 = Tick(f"evt 2", unit=TimeUnit.ns)
    event_recorder.add(tick_2)
    assert len(event_recorder.get_all()) == 2

    converted_event_recorder: EventRecorder = event_recorder.to(TimeUnit.ms)
    for event in converted_event_recorder.get_all():
        assert event.unit == TimeUnit.ms
