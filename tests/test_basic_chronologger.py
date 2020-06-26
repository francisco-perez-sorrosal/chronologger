import math
import time

from chronologger import Timer
from chronologger.model import Chronologger, TimeUnit

sleep_time_seconds = 1


def test_chronologger_logs_elapsed_time(capsys):
    # Basic timer functionality!
    timer = Chronologger()
    timer.start()
    time.sleep(sleep_time_seconds)  # Simulate some time has passed...
    period = timer.stop(reset=True)
    assert period.unit == TimeUnit.s
    assert math.isclose(period.time(), sleep_time_seconds, rel_tol=0.02)


def test_chronologger_log_repoting(capsys):
    timer = Chronologger()
    timer.start()
    timer.stop(reset=True)
    # assert False
    captured = capsys.readouterr()  # As default option in .stop() above does not log any message, then...
    assert "elapsed time" not in captured.out

    # This time log the standard message
    timer.start(start_tick_name="st")
    timer.stop(do_log=True, final_tick_name="ft")
    captured = capsys.readouterr()
    assert "elapsed time" in captured.out
    print(captured.out)

    # Check extended log messages
    timer = Chronologger(name='explicit_name', simple_log_msgs=False)
    assert timer.name == "explicit_name"
    timer.start(start_tick_name="st1")
    timer.stop(do_log=True, final_tick_name="ft1")
    captured = capsys.readouterr()
    assert "elapsed time" in captured.out
    assert "st1" in captured.out
    assert "ft1" in captured.out

# TODO: Differentiate (and separate) Timer from Logger tests
def test_as_context_manager(capsys):
    with Timer("test"):
        time.sleep(0)
    captured = capsys.readouterr()
    assert "test_start_tick" not in captured.out
    assert "test_end_tick" not in captured.out

    with Timer("test", log_when_exiting=True):
        time.sleep(0)
    captured = capsys.readouterr()
    assert "test_start_tick" in captured.out
    assert "test_end_tick" in captured.out

# TODO: Differentiate (and separate) Timer from Logger tests
def test_as_decorator(capsys):
    @Timer("test")
    def dummy():
        time.sleep(0)

    dummy()
    captured = capsys.readouterr()
    assert "test_start_tick" not in captured.out
    assert "test_end_tick" not in captured.out

    @Timer("test", log_when_exiting=True)
    def dummy():
        time.sleep(0)

    dummy()
    captured = capsys.readouterr()
    assert "test_start_tick" in captured.out
    assert "test_end_tick" in captured.out

# TODO: Differentiate (and separate) Timer from Logger tests
def test_unit_conversion(capsys):
    timer = Timer("test", unit=TimeUnit.ns).start()
    time.sleep(sleep_time_seconds)  # Simulate some time has passed...
    period = timer.stop(do_log=True)
    print(period)
    captured = capsys.readouterr()
    print(captured.out)
    print(sleep_time_seconds * 10 ** timer.chrono.unit.value)
    assert math.isclose(period.time(), sleep_time_seconds * 10 ** timer.chrono.unit.value, rel_tol=0.02)
    assert timer.chrono.unit.name in captured.out

# TODO: Differentiate (and separate) Timer from Logger tests
def test_marks(capsys):
    sleep_time_seconds = 0.1  # 100 ms
    timer = Timer(name="Test Loop!", unit=TimeUnit.ms).start("time to start loop")
    for i in range(3):
        time.sleep(sleep_time_seconds)
        timer.mark("i={}".format(i))
    period = timer.stop()
    print(timer.chrono.unit.from_secs(sleep_time_seconds * 3))
    assert math.isclose(period.elapsed(), timer.chrono.unit.from_secs(sleep_time_seconds * 3), rel_tol=0.1)

    print(timer)
    captured = capsys.readouterr()
    for i in range(3):
        assert "i={}".format(i) in captured.out

    with Timer(name="Test Loop in context!",
                      unit=TimeUnit.ms,
                      log_when_exiting=True,
                      simple_log=False) as timer:
        for j in range(3):
            time.sleep(sleep_time_seconds)
            timer.mark("j={}".format(j))

    captured = capsys.readouterr()
    for i in range(3):
        assert "j={}".format(i) in captured.out
