from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic

from src.config import Config

TSnapshot = TypeVar('TSnapshot')

class Backend(ABC, Generic[TSnapshot]):
    def __init__(self, config: Config, progress_callback: Callable[[str, int], None], savepoint_callback: Callable[[TSnapshot], None]):
        self.config = config
        self.progress_callback = progress_callback
        self.savepoint_callback = savepoint_callback

    @abstractmethod
    def start(self, snapshot: TSnapshot | None = None):
        ...
