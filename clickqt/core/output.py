from io import BytesIO, TextIOWrapper 
from PySide6.QtWidgets import QPlainTextEdit, QMenu
from PySide6.QtGui import QTextCursor, QColor, QContextMenuEvent, QAction
from PySide6.QtCore import Signal
import html

class OutputStream(TextIOWrapper):
    """
        Redirects a stream (here: stdout and stderr) to a TerminalOutput  
    """
    def __init__(self, output: "TerminalOutput", old_stream: TextIOWrapper, color: QColor=QColor("black")):
        super().__init__(BytesIO(), "utf-8")
        self.output = output
        self.old_stream = old_stream
        self.color = color

    def write(self, message: bytes|str):
        if message:
            message = message.decode("utf-8") if isinstance(message, bytes) else message
            print(message, file=self.old_stream, end="") # Write to "normal" stream as well
            message = html.escape(message).replace("\r\n", "\n").replace("\n", "<br>") # Replace '\n' with HTML code

            # Send new message to main thread because worker thread could also be here (-> program crash otherwise)
            self.output.newHtmlMessage.emit(f"<p span style='color: rgb({self.color.red()}, {self.color.green()}, {self.color.blue()})'>{message}</p>")

class TerminalOutput(QPlainTextEdit):
    """
        QPlainTextEdit with extended context menu (clearing output)
    """
    newHtmlMessage = Signal(str)

    def contextMenuEvent(self, event: QContextMenuEvent): # pragma: no cover
        menu: QMenu = self.createStandardContextMenu()
        action = QAction("Clear")
        menu.addAction(action)
        action.triggered.connect(lambda: self.clear())
        menu.exec(event.globalPos())

    def writeHtml(self, message:str):
        self.moveCursor(QTextCursor.End)
        self.textCursor().insertHtml(message)