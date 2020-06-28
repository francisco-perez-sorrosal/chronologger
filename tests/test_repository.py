from chronologger import Tick, Timer, TimeUnit, root_repo
from chronologger.repository import TimeRepository, RootTimeRepository


def test_root_repo_is_initialized():
    assert isinstance(root_repo, RootTimeRepository)
    assert root_repo.name == 'root'


def test_nodes_at_root_level():
    root_timer = Timer("root")
    repo = TimeRepository(root_timer)

    t1 = Tick("phase 1", root_timer)
    t2 = Tick("phase 2", root_timer)
    t3 = Tick("phase 3", root_timer)

    repo.add(t1)
    repo.add(t2)
    repo.add(t3)

    events = repo.get_all()
    assert events == list([t1, t2, t3])


def test_nested_nodes_1_level():
    root_timer = Timer("root")
    repo = TimeRepository(root_timer)

    t1 = Tick("tick 1", root_timer)
    repo.add(t1)

    events = repo.get_all()
    assert events == list([t1])

    p1_timer = Timer("phase_1", unit=TimeUnit.ms, parent_ctx=root_timer)
    repo.register(p1_timer)

    repo.add(Tick("simulated tick 1.1", p1_timer))
    repo.add(Tick("simulated tick 1.2", p1_timer))

    events = repo.get_all()
    assert len(
        events) == 3  # TODO For now it's a flat structure and we can't check nested timer contents as we have to invoke the service

    assert len(repo.time_contexts) == 2
