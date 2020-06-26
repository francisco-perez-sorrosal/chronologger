import time

from chronologger import main_timer
from chronologger.timer import Timer


@Timer(name="sub_method", parent_ctx=main_timer)
def sub_method():
    time.sleep(0.1)


@Timer(name="main", parent_ctx=main_timer)
def main():
    sub_method()
    time.sleep(0.1)


if __name__ == "__main__":
    print("=========================================================================================================")
    print("   STARTING!!!")
    print("=========================================================================================================")
    main()
    print("=========================================================================================================")
    print("   PRINTING TIME")
    print("=========================================================================================================")
    main_timer.print()
    print("=========================================================================================================")
