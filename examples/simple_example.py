import time

from chronologger import Timer, TimeUnit, root_timer


# Example of decorator: This should report ~100ms each time that is called
@Timer(name="Foo method!", unit=TimeUnit.ms, simple_log=True)
def foo():
    time.sleep(0.1)


def main():
    # Example of explicit timer: This should report ~100ms
    timer = Timer("Individual Timer", unit=TimeUnit.ms).start()
    time.sleep(0.1)
    timer.stop()

    # Example of explicit context timer: This should report ~1s
    with Timer(name="Test Loop!", unit=TimeUnit.s, simple_log=True) as timer:
        for i in range(5):
            time.sleep(0.1)  # e.g. simulate IO
            foo()
            timer.mark("i_{}".format(i))


if __name__ == "__main__":
    root_timer.label("   STARTING!!!")
    main()
    root_timer.label("   PRINTING TIME")
    root_timer.print()
