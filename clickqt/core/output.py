from PySide6.QtWidgets import QPlainTextEdit
from io import BytesIO, TextIOWrapper
from PySide6.QtGui import QTextCursor
import sys

class Output(TextIOWrapper):
        """
            Redirects a stream (here: stdout) to a QPlainTextEdit   
        """
        def __init__(self, output: QPlainTextEdit):
            super().__init__(BytesIO(), sys.stdout.encoding)
            self.output = output
            
        def write(self, message: bytes|str):
            if message:
                message = message.decode(sys.stdout.encoding) if isinstance(message, bytes) else message  
                self.output.moveCursor(QTextCursor.End)
                self.output.insertPlainText(message)