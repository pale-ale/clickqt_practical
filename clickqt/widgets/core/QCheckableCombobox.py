# Credits to https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
from __future__ import annotations

import typing as t

from PySide6.QtWidgets import QComboBox, QStyledItemDelegate
from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtGui import QStandardItem


class QCheckableComboBox(QComboBox):
    """Combobox with checkable items."""

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Use custom delegate
        self.setItemDelegate(QCheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent):
        if obj == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return event.type() == QEvent.Type.Wheel

        if obj == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        """Updates the text displayed in the combobox."""

        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                texts.append(self.model().item(i).text())

        self.lineEdit().setText(", ".join(texts))

        # Compute elided text (with "...")
        # metrics = QFontMetrics(self.lineEdit().font())
        # elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, self.lineEdit().width())
        # self.lineEdit().setText(elidedText)

    def addItem(self, text: str):
        """Adds the string in **text** to the checkable combobox and unchecks the added item."""

        item = QStandardItem()
        item.setText(text)
        item.setData(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts: t.Iterable[str]):
        """Adds each of the strings in **texts** to the checkable combobox."""

        for text in texts:
            self.addItem(text)

    def checkItems(self, texts: t.Iterable[str]):
        """Checks every item in **texts**, all other items will be unchecked."""

        for i in range(self.model().rowCount()):
            if self.model().item(i).data().upper() in texts:
                self.model().item(i).setCheckState(Qt.CheckState.Checked)
            else:
                self.model().item(i).setCheckState(Qt.CheckState.Unchecked)

        self.updateText()

    def getData(self) -> t.Iterable[str]:
        """Returns the names of all checked items."""

        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                res.append(self.model().item(i).data())
        return res
