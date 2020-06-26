from chronologger import Tick
from chronologger.repository import TimeRepository, TimeEventTypes, RootTimeRepository


def test_orphan_nodes():
    repo = TimeRepository("test_repo")

    t1 = Tick("phase 1")
    t2 = Tick("phase 2")
    t3 = Tick("phase 3")

    repo.add(t1)
    repo.add(t2)
    repo.add(t3)

    events = repo.get_all()
    print(repo.name)
    assert events == list([t1, t2, t3])
    assert repo.get_all(TimeEventTypes.orphan) == events
    assert repo.get_all(TimeEventTypes.orphan, include_root=False) == events


def test_nested_nodes_1_level():
    repo = TimeRepository("test_repo")
    root_tick = Tick("root_tick")
    repo.register_root(root_tick)

    t1 = Tick("phase 1")
    t2 = Tick("phase 2")
    t3 = Tick("phase 3")

    repo.add(t1, "root_tick")
    repo.add(t2, "root_tick")
    repo.add(t3, "root_tick")

    events = repo.get_all(include_root=True)
    assert events == list([root_tick, t1, t2, t3])
    assert repo.get_all(TimeEventTypes.regular) == events

    events = repo.get_all(include_root=False)
    assert events == list([t1, t2, t3])
    assert repo.get_all(TimeEventTypes.regular, include_root=False) == events


def test_nested_nodes_1_level():

    repo = TimeRepository("test_repo")
    root_tick = Tick("root_tick")
    repo.register_root(root_tick)

    t1 = Tick("phase 1")
    t11 = Tick("phase 1.1")
    t12 = Tick("phase 1.2")

    repo.add(t1, "root_tick")
    repo.add(t11, "phase 1")
    repo.add(t12, "phase 1")

    events = repo.get_all(include_root=False)
    assert events == list([t1, t11, t12])


def test_root_repo():
    repo = RootTimeRepository("test_root_repo")
    assert repo.name == 'test_root_repo'
    assert len(repo.get_all()) == 1
    assert repo.get_all()[0].name == 'root'
