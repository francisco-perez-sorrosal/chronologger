import math
import time

from chronologger import Chronologger, TimeUnit

sleep_time_seconds = 1


def test_basic_functionality(capsys):
    # Basic timer functionality!
    timer = Chronologger()
    timer.start()
    time.sleep(sleep_time_seconds)  # Simulate some time has passed...
    _, elapsed_seconds = timer.stop(reset=True)
    assert math.isclose(elapsed_seconds, sleep_time_seconds, rel_tol=0.02)

    captured = capsys.readouterr()  # As default option in .stop() above does not log any message, then...
    assert "elapsed" not in captured.out

    # This time log the standard message
    timer.start()
    timer.stop(do_log=True)
    captured = capsys.readouterr()
    assert "elapsed" in captured.out


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


def test_user_specific_messages(capsys):
    common_text = "Satancisco takes"
    dummy_text = common_text + " {}"

    timer = Chronologger(text=dummy_text).start()
    timer.stop(do_log=True)

    captured = capsys.readouterr()
    assert common_text in captured.out


def test_unit_conversion(capsys):
    timer = Chronologger(unit=TimeUnit.ns).start()
    time.sleep(sleep_time_seconds)  # Simulate some time has passed...
    _, elapsed = timer.stop(do_log=True)
    captured = capsys.readouterr()
    assert math.isclose(elapsed, sleep_time_seconds * 10 ** timer.unit.value, rel_tol=0.02)
    assert timer.unit.name in captured.out


def test_marks(capsys):
    sleep_time_seconds = 0.1 # 100 ms
    timer = Chronologger(name="Test Loop!", unit=TimeUnit.ms).start("time to start loop")
    for i in range(3):
        time.sleep(sleep_time_seconds)
        timer.mark("i={}".format(i))
    _, elapsed = timer.stop()
    assert math.isclose(elapsed, timer.unit.from_secs(sleep_time_seconds * 3), rel_tol=0.1)
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
