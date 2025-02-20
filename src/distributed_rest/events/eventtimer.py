from distributed_rest.events.baseevent import BaseEvent

from threading import Lock, Timer
from typing import Optional


class EventTimerMeta(type):
    """
    Metaclass for creating a singleton EventTimer with thread lock.

    This metaclass ensures that only one instance of the EventTimer class is created.
    It uses a thread lock to ensure thread safety during the instantiation process.

    Attributes:
        _instances (dict): Dictionary to store the singleton instance.
        _lock (Lock): Thread lock to ensure thread safety.

    Methods:
        __call__(cls, *args, **kwargs): Controls the instantiation of the EventTimer class.
    """
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Controls the instantiation of the EventTimer class.

        This method ensures that only one instance of the EventTimer class is created.
        It uses a thread lock to ensure thread safety during the instantiation process.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            EventTimer: The singleton instance of the EventTimer class.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class EventTimer(metaclass=EventTimerMeta):
    """
    A singleton timer class that repeatedly invokes a callback function at specified intervals.

    Attributes:
        who (str): Identifier for the timer instance.
        active (bool): Indicates whether the timer is currently active.
        on_timer_elapsed (BaseEvent): Event that is fired when the timer elapses.
        _interval (int): Interval in seconds between timer events.
        _timer (Optional[Timer]): Internal threading.Timer instance.

    Methods:
        start() -> None: Starts the timer.
        stop() -> None: Stops the timer.
    """

    def __init__(self, interval: int):
        """
        Initializes the EventTimer with a specified interval.

        Args:
            interval (int): The interval in seconds between timer events. Must be a positive number.

        Raises:
            ValueError: If the interval is not a positive number.
        """
        if interval <= 0:
            raise ValueError("Interval must be a positive number")

        self.who: str = 'EventTimer'
        self.active: bool = False
        self.on_timer_elapsed = BaseEvent()

        self._interval: int = interval
        self._timer: Optional[Timer] = None

    def _run(self):
        """Internal method to fire the event and restart the timer."""
        self.on_timer_elapsed._fire()
        self._timer = Timer(self._interval, self._run)
        self._timer.start()

    def start(self) -> None:
        """Starts the timer."""
        if self.active:
            return
        if not self._timer:
            self._timer = Timer(self._interval, self._run)
        self._timer.start()
        self.active = True


    def stop(self) -> None:
        """Stops the timer."""
        if self._timer:
            self._timer.cancel()
        self.active = False

