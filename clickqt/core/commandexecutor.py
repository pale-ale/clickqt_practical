import click
from PySide6.QtCore import Signal, QObject, Slot
from typing import Callable, Iterable

class CommandExecutor(QObject):
    """
        Worker which executes the callback commands
    """
    finished = Signal()

    @Slot(list, click.Context)
    def run(self, tasks:Iterable[Callable], ctx:click.Context): # pragma: no cover; Tested in test_execution.py
        # Push context of selected command, needed for @click.pass_context and @click.pass_obj
        click.globals.push_context(ctx) 

        for task in tasks:
            task()
        
        self.finished.emit()