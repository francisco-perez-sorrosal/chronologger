import time

import chronologger
import chronologger.service

repo = chronologger.service.getRepository()


# @Chronologger(name="Foo method!", unit=TimeUnit.ms, simple_log_msgs=False, log_when_exiting_context=True)
def dummy_1():
    time.sleep(0.1)
