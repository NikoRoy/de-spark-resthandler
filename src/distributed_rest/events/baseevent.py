from typing import List, Callable


class BaseEvent:
    def __init__(self):
        self.type = 'BaseEvent'
        self._subscriptions: List[Callable] = []

    def subscribe(self, handler: Callable) -> None:
        self._subscriptions.append(handler)

    def unsubscribe(self, handler: Callable) -> None:
        self._subscriptions.remove(handler)

    def _fire(self, *args, **kwargs) -> None:
        for handler in self._subscriptions:
            handler(*args, **kwargs)
