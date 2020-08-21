import time

from chronologger import Timer, TimeUnit


@Timer(name="Foo method in module!", unit=TimeUnit.ms, simple_log=True)
def foo():
    time.sleep(0.1)
