import math
import time
import unittest.mock as mock

from chronologger.model import Tick, TimeUnit, EventRecorder, TimeEvent, Period

time_event_name = "tick"


@mock.patch("chronologger.Timer")
def test_tick_basic_properties(mock_timer):
    tick = Tick(time_event_name, mock_timer)
    assert isinstance(tick, TimeEvent)
    assert isinstance(tick, Tick)
    assert tick.name == time_event_name
    assert tick.unit == TimeUnit.s
    now = time.perf_counter()
    assert tick.time() < now


@mock.patch("chronologger.Timer")
def test_tick_conversions(mock_timer):
    tick = Tick(time_event_name, mock_timer)

    tick_in_secs_again = tick.to(TimeUnit.s)
    assert tick_in_secs_again == tick

    tick_ms = tick.to(TimeUnit.ms)
    assert tick_ms.name == tick.name
    assert tick_ms.unit == TimeUnit.ms
    assert math.isclose(tick_ms.time(), TimeUnit.ms.from_secs(tick.time()), rel_tol=0.02)

    tick_ns = tick.to(TimeUnit.ns)
    assert tick_ns.name == tick.name
    assert tick_ns.unit == TimeUnit.ns
    assert math.isclose(tick_ns.time(), TimeUnit.ns.from_secs(tick.time()), rel_tol=0.02)
    now_in_ns = TimeUnit.ns.from_secs(time.perf_counter())
    assert tick_ns.time() < now_in_ns


@mock.patch("chronologger.Timer")
def test_two_ticks_with_the_same_name_are_different_as_they_have_different_timestamps(mock_timer):
    tick_1 = Tick("tock", mock_timer)
    tick_2 = Tick("tock", mock_timer)
    assert not tick_1 == tick_2
    assert tick_1.time() < tick_2.time()


@mock.patch("chronologger.Timer")
def test_basic_homogeneus_period(mock_timer):
    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tock", mock_timer)

    explicit_period = Period("test_period", mock_timer, TimeUnit.s, tick_1, tick_2)
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


@mock.patch("chronologger.Timer")
def test_basic_heterogeneous_period(mock_timer, capsys):
    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tock", mock_timer, TimeUnit.ns)

    period_name = "test_period"
    explicit_period_ms = Period(period_name, mock_timer, TimeUnit.ms, tick_1, tick_2)
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


@mock.patch("chronologger.Timer")
def test_heterogeneous_period_gets_converted_properly_to_homogeneous(mock_timer, capsys):
    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tock", mock_timer, TimeUnit.ns)

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


# TODO The next four tests can be combined using text fixtures and validation data passed as arguments
@mock.patch("chronologger.Timer")
def test_homogeneous_explicit_period_creation(mock_timer, capsys):
    """This should test that the conversions and calculations are correct
    given that the main time unit driving the process is the one that
    corresponds to the first period. As all the ticks are explicitly passed,
    no conversions are needed"""

    driver_time_unit = TimeUnit.s

    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tack", mock_timer)

    explicit_period_1 = Period("period_1", mock_timer, driver_time_unit, tick_1, tick_2)

    sleep_time_secs = 0.1  # 100 ms
    tick_3 = Tick("tock", mock_timer)
    time.sleep(sleep_time_secs)
    tick_4 = Tick("tuck", mock_timer)

    explicit_period_2 = Period("period_2", mock_timer, TimeUnit.s, tick_3, tick_4)

    combined_explicit_period = Period("new_period", mock_timer, TimeUnit.s, explicit_period_1.start,
                                      explicit_period_2.end)

    assert combined_explicit_period.name == "new_period"
    assert combined_explicit_period.unit == driver_time_unit
    assert combined_explicit_period.start == tick_1
    assert combined_explicit_period.end == tick_4


@mock.patch("chronologger.Timer")
def test_homogeneous_calculated_period_difference(mock_timer, capsys):
    """This should test that the conversions and calculations are correct
    given that the main time unit driving the process is the one that
    corresponds to the first period. As all the ticks involved are
    homogeneous with regard to the time units, no conversions are needed"""

    driver_time_unit = TimeUnit.s

    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tack", mock_timer)

    explicit_period_1 = Period("period_1", mock_timer, driver_time_unit, tick_1, tick_2)

    sleep_time_secs = 0.1  # 100 ms
    tick_3 = Tick("tock", mock_timer)
    time.sleep(sleep_time_secs)
    tick_4 = Tick("tuck", mock_timer)

    explicit_period_2 = Period("period_2", mock_timer, TimeUnit.s, tick_3, tick_4)

    combined_calculated_period = explicit_period_2 - explicit_period_1

    assert combined_calculated_period.name == f"elapsed ({tick_4.name} - {tick_1.name})"
    assert combined_calculated_period.unit == driver_time_unit
    assert combined_calculated_period.start == tick_1
    assert combined_calculated_period.end == tick_4


@mock.patch("chronologger.Timer")
def test_heterogeneous_explicit_period_creation(mock_timer, capsys):
    """This should test that the conversions and calculations are correct
    given that the main time unit driving the process is the one that
    corresponds to the first period. As all the ticks involved are
    homogeneous with regard to the time units, no conversions are needed"""

    driver_time_unit = TimeUnit.s

    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer, TimeUnit.ns)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tack", mock_timer, TimeUnit.ms)

    explicit_period_1 = Period("period_1", mock_timer, driver_time_unit, tick_1, tick_2)

    sleep_time_secs = 0.1  # 100 ms
    tick_3 = Tick("tock", mock_timer, TimeUnit.ns)
    time.sleep(sleep_time_secs)
    tick_4 = Tick("tuck", mock_timer, TimeUnit.ms)

    explicit_period_2 = Period("period_2", mock_timer, TimeUnit.ms, tick_3, tick_4)

    combined_calculated_period = Period("new_period", mock_timer, driver_time_unit, explicit_period_1.start,
                                        explicit_period_2.end)

    assert combined_calculated_period.name == f"new_period"
    assert combined_calculated_period.unit == driver_time_unit
    assert combined_calculated_period.start.name == tick_1.name
    assert combined_calculated_period.start.unit == tick_1.unit
    assert combined_calculated_period.end.name == tick_4.name
    assert combined_calculated_period.end.unit == tick_4.unit


@mock.patch("chronologger.Timer")
def test_heterogeneous_calculated_period_difference(mock_timer, capsys):
    """This should test that the conversions and calculations are correct
    given that the main time unit driving the process is the one that
    corresponds to the first period. Conversions of the ticks involved
    are expected"""

    driver_time_unit = TimeUnit.s

    sleep_time_secs = 0.1  # 100 ms
    tick_1 = Tick("tick", mock_timer, TimeUnit.ns)
    time.sleep(sleep_time_secs)
    tick_2 = Tick("tack", mock_timer, TimeUnit.ms)

    explicit_period_1 = Period("period_1", mock_timer, driver_time_unit, tick_1, tick_2)

    sleep_time_secs = 0.1  # 100 ms
    tick_3 = Tick("tock", mock_timer, TimeUnit.ns)
    time.sleep(sleep_time_secs)
    tick_4 = Tick("tuck", mock_timer, TimeUnit.ms)

    explicit_period_2 = Period("period_2", mock_timer, TimeUnit.ms, tick_3, tick_4)

    combined_calculated_period = explicit_period_2 - explicit_period_1

    assert combined_calculated_period.name == f"elapsed ({tick_4.name} - {tick_1.name})"
    assert combined_calculated_period.unit == driver_time_unit
    assert combined_calculated_period.start.name == tick_1.name
    assert combined_calculated_period.start.unit == driver_time_unit
    assert combined_calculated_period.end.name == tick_4.name
    assert combined_calculated_period.end.unit == driver_time_unit


@mock.patch("chronologger.Timer")
def test_event_recorder_can_hold_and_retrieve_events(mock_timer):
    num_of_time_events_to_create = 3
    event_recorder = EventRecorder()
    for i in range(0, num_of_time_events_to_create):
        event_recorder.add(Tick(f"evt {i}", mock_timer))
        time.sleep(0.1)
    assert len(event_recorder.get_all()) == num_of_time_events_to_create


@mock.patch("chronologger.Timer")
def test_event_recorder_can_homogeinize_different_event_time_units(mock_timer):
    event_recorder = EventRecorder()
    tick_1 = Tick(f"evt 1", mock_timer, unit=TimeUnit.s)
    event_recorder.add(tick_1)
    time.sleep(0.1)
    tick_2 = Tick(f"evt 2", mock_timer, unit=TimeUnit.ns)
    event_recorder.add(tick_2)
    assert len(event_recorder.get_all()) == 2

    converted_event_recorder: EventRecorder = event_recorder.to(TimeUnit.ms)
    for event in converted_event_recorder.get_all():
        assert event.unit == TimeUnit.ms
