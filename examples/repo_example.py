import time

from chronologger.timer import Timer, root_timer


@Timer(name="sub_method", parent_ctx=root_timer)
def sub_method():
    time.sleep(0.1)


@Timer(name="main", parent_ctx=root_timer)
def main():
    sub_method()
    time.sleep(0.1)


if __name__ == "__main__":
    root_timer.label("   STARTING!!!")
    main()
    root_timer.label("   PRINTING TIME")
    root_timer.print()
