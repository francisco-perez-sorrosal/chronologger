import time

from chronologger import Chronologger, TimeUnit


@Chronologger(name="Foo method!", unit=TimeUnit.ms, simple_log_msgs=False, log_when_exiting_context=True)
def foo():
    time.sleep(0.1)


def main():
    with Chronologger(name="Test Loop!", unit=TimeUnit.s,
                      simple_log_msgs=False, log_when_exiting_context=True).start() as timer:
        for i in range(3):
            time.sleep(0.1)  # e.g. simulate IO
            foo()
            timer.mark("i_{}".format(i))


if __name__ == "__main__":
    main()
