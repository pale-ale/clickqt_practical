from PySide6.QtCore import Signal, QObject, Slot
from typing import Callable, Iterable

class CommandExecutor(QObject):
    """
        Worker which executes the callback commands
    """
    finished = Signal()

    @Slot(list)
    def run(self, tasks:Iterable[Callable]): # pragma: no cover; Tested in test_execution.py
        for task in tasks:
            task()
        
        self.finished.emit()