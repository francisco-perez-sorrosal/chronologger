import time

from chronologger import Timer, TimeUnit
from chronologger import root_timer
from examples import dummy_module


def main():
    # Example of explicit timer: This should report ~100ms
    timer = Timer("Individual Timer", unit=TimeUnit.ms).start()
    time.sleep(0.1)
    timer.stop()

    # Example of explicit context timer: This should report ~1s
    with Timer(name="Test Loop calling module!", unit=TimeUnit.s, simple_log=True) as timer:
        for i in range(5):
            time.sleep(0.1)  # e.g. simulate IO
            dummy_module.foo()
            timer.mark("i_{}".format(i))


if __name__ == "__main__":
    root_timer.label("   STARTING!!!")
    main()
    root_timer.label("   PRINTING TIME")
    root_timer.print()
