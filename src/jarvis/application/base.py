from threading import Lock
from typing import ClassVar


class SingletonMeta(type):
    """
    Thread-safe implementation of the Singleton pattern.
    """

    _instances: ClassVar = {}

    _lock: Lock = Lock()

    """
    We now have a lock object that will be used to synchronize threads during 
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]
