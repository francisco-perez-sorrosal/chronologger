import time

from chronologger import Timer, TimeUnit


@Timer(name="Foo method!", unit=TimeUnit.ms, simple_log=True, log_when_exiting=True)
def foo():
    time.sleep(0.1)


def main():
    with Timer(name="Test Loop!", unit=TimeUnit.s,
               simple_log=True, log_when_exiting=True).start() as timer:
        for i in range(3):
            time.sleep(0.1)  # e.g. simulate IO
            foo()
            timer.mark("i_{}".format(i))


if __name__ == "__main__":
    main()
