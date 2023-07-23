from __future__ import annotations

from io import BytesIO, TextIOWrapper
import html

from PySide6.QtWidgets import QPlainTextEdit, QMenu
from PySide6.QtGui import QTextCursor, QContextMenuEvent, QAction, QColor
from PySide6.QtCore import Signal


class OutputStream(TextIOWrapper):
    """Sends the content of **stream** as Html-escaped-text to **output**.

    :param output: The object to which the content of **stream** should be sent
    :param stream: The stream-object from which the content should be taken
    :param color: The display color used in **output**
    """

    def __init__(self, output: "TerminalOutput", stream: TextIOWrapper, color: QColor):
        super().__init__(BytesIO(), "utf-8")
        self.output = output
        self.stream = stream
        self.color = color

    def write(self, message: "bytes | str"):
        """Writes **message** to **output** and utf-8 decoded + Html-escaped to **stream**

        :param message: The message which should be written to **output** and **stream**
        """

        if message:
            message = message.decode("utf-8") if isinstance(message, bytes) else message
            print(message, file=self.stream, end="")  # Write to "normal" stream as well
            message = (
                html.escape(message).replace("\r\n", "\n").replace("\n", "<br>")
            )  # Replace '\n' with HTML code

            # Send new message to main thread because worker thread could also be here (-> program crash otherwise)
            self.output.newHtmlMessage.emit(
                f"<p span style='color: rgb({self.color.red()}, {self.color.green()}, {self.color.blue()})'>{message}</p>"
            )


class TerminalOutput(QPlainTextEdit):
    """Displays the output on the screen. Extends the standard context menu with a 'clear'-function."""

    newHtmlMessage: Signal = Signal(
        str
    )  #: Internal Qt-Signal, which will be emitted when there is a new Html-message to display

    def contextMenuEvent(self, event: QContextMenuEvent):  # pragma: no cover
        """Inherited from :class:`~PySide6.QtWidgets.QPlainTextEdit`\n
        Extends the standard context menu with a 'clear'-function.
        """

        menu: QMenu = self.createStandardContextMenu()
        action = QAction("Clear")
        menu.addAction(action)
        action.triggered.connect(self.clear)
        menu.exec(event.globalPos())

    def writeHtml(self, message: str):
        """Appends **message** to the end of the current content.

        :param message: The message in Html-format that should be appended to the end of the current content
        """

        self.moveCursor(QTextCursor.End)
        self.textCursor().insertHtml(message)
