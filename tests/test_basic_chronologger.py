import math
import time

from chronologger import Chronologger
from chronologger.model import TimeUnit

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
    assert "elapsed" not in captured.out

    # This time log the standard message
    timer.start()
    timer.stop(do_log=True)
    captured = capsys.readouterr()
    assert "elapsed" in captured.out
    print(captured.out)

    # Check extended log messages
    timer = Chronologger(name='explicit_name', simple_log_msgs=False)
    assert timer.name == "explicit_name"
    timer.start()
    timer.stop(do_log=True)
    captured = capsys.readouterr()
    assert "elapsed" in captured.out
    assert "start_tick" in captured.out
    assert "end_tick" in captured.out


def test_as_context_manager(capsys):
    with Chronologger():
        time.sleep(0)
    captured = capsys.readouterr()
    assert "elapsed" not in captured.out

    with Chronologger(log_when_exiting_context=True):
        time.sleep(0)
    captured = capsys.readouterr()
    assert "elapsed" in captured.out


def test_as_decorator(capsys):
    @Chronologger()
    def dummy():
        time.sleep(0)

    dummy()
    captured = capsys.readouterr()
    assert "elapsed" not in captured.out

    @Chronologger(log_when_exiting_context=True)
    def dummy():
        time.sleep(0)

    dummy()
    captured = capsys.readouterr()
    assert "elapsed" in captured.out


def test_unit_conversion(capsys):
    timer = Chronologger(unit=TimeUnit.ns).start()
    time.sleep(sleep_time_seconds)  # Simulate some time has passed...
    period = timer.stop(do_log=True)
    print(period)
    captured = capsys.readouterr()
    print(captured.out)
    print(sleep_time_seconds * 10 ** timer.unit.value)
    assert math.isclose(period.time(), sleep_time_seconds * 10 ** timer.unit.value, rel_tol=0.02)
    assert timer.unit.name in captured.out


def test_marks(capsys):
    sleep_time_seconds = 0.1  # 100 ms
    timer = Chronologger(name="Test Loop!", unit=TimeUnit.ms).start("time to start loop")
    for i in range(3):
        time.sleep(sleep_time_seconds)
        timer.mark("i={}".format(i))
    period = timer.stop()
    print(timer.unit.from_secs(sleep_time_seconds * 3))
    assert math.isclose(period.elapsed(), timer.unit.from_secs(sleep_time_seconds * 3), rel_tol=0.1)

    print(timer)
    captured = capsys.readouterr()
    for i in range(3):
        assert "i={}".format(i) in captured.out

    with Chronologger(name="Test Loop in context!",
                      unit=TimeUnit.ms,
                      log_when_exiting_context=True,
                      simple_log_msgs=False) as timer:
        for j in range(3):
            time.sleep(sleep_time_seconds)
            timer.mark("j={}".format(j))

    captured = capsys.readouterr()
    for i in range(3):
        assert "j={}".format(i) in captured.out
