from .model import TimeUnit, Tick, Period, TimeContext, TimeEvent
from .repository import init_repo
from .timer import Timer

main_timer = Timer(name="root")
repository.init_repo(main_timer)
