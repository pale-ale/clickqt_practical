import click
from PySide6.QtCore import Signal, QObject, Slot
from typing import Callable, Iterable

class CommandExecutor(QObject):
    """Worker which executes the received tasks/callbacks"""

    finished:Signal = Signal() #:Internal Qt-signal, which will be emitted when the run(...)-Slot has finished

    @Slot(list, click.Context)
    def run(self, tasks:Iterable[Callable], ctx:click.Context): # pragma: no cover; Tested in test_execution.py
        """Pushes the current context on the click internal stack and executes the received tasks.
        When the execution is done, the finished signal will be emitted

        :param tasks: The callbacks to execute
        :param ctx: The current context which should be pushed on the click internal stack
        """

        # Push context of selected command, needed for @click.pass_context and @click.pass_obj
        click.globals.push_context(ctx) 

        for task in tasks:
            task()
        
        self.finished.emit()