import sys
from io import BytesIO, TextIOWrapper 
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QTextCursor, QColor
import html

class Output(TextIOWrapper):
        """
            Redirects a stream (here: stdout) to a QPlainTextEdit   
        """
        def __init__(self, output: QPlainTextEdit, color: QColor=QColor("black")):
            super().__init__(BytesIO(), sys.stdout.encoding)
            self.output = output
            self.color = color

        def write(self, message: bytes|str):
            if message:
                message = message.decode(sys.stdout.encoding) if isinstance(message, bytes) else message  
                message = message.replace("\r\n", "\n").replace("\n", "<br>") # Repalce '\n' with HTML code
                self.output.moveCursor(QTextCursor.End)
                self.output.textCursor().insertHtml(f"<p span style='color: rgb({self.color.red()}, {self.color.green()}, {self.color.blue()})'>{message}</p>")
