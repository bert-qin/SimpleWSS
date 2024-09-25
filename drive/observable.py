class Observer:

    def update_observer(self, *args, **kwargs):
        pass


class Observable:

    def __init__(self) -> None:
        self._observer_set = set()

    def register_observer(self, observer):
        self._observer_set.add(observer)

    def unregister_observer(self, observer: Observer = None):
        if observer:
            self._observer_set.discard(observer)
        else:
            self._observer_set.clear()

    def notify_all(self, *args, **kwargs):
        for o in self._observer_set:
            o.update_observer(*args, **kwargs)
