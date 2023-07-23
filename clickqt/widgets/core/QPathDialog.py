from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QTreeView,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QDialog,
)
from PySide6.QtCore import QObject, QEvent, SIGNAL, QDir, Slot


class QPathDialog(QFileDialog):
    """A file dialog that accepts a single file or a single directory.

    :param parent: The parent Qt-widget, defaults to None
    :param directory: The directory that will be displayed when opening the dialog, defaults to the current path
    :param exist: Specifies, whether the file / directory has to exist
    """

    def __init__(
        self,
        parent: "QWidget | None" = None,
        directory: str = QDir.currentPath(),
        exist: bool = True,
    ):
        super().__init__(parent, directory=directory)

        self.exist = exist
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.FileMode.Directory)
        self.open_button: QPushButton = None
        # self.list_view: QListView = self.findChild(QListView, "listView")
        # if self.list_view:
        #    self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree_view: QTreeView = self.findChild(QTreeView)
        # if self.tree_view:
        #    self.tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.selected_path: str = ""
        self.base_dir: str = ""

        for btn in self.findChildren(QPushButton):
            text = btn.text().lower()
            if "open" in text or "choose" in text:
                self.open_button = btn
                break

        if self.open_button:
            self.open_button.installEventFilter(self)
            self.disconnect(self.open_button, SIGNAL("clicked()"))
            self.open_button.clicked.connect(self.openClicked)

    def selectedPath(self) -> str:
        """Returns the selected path."""

        return self.selected_path

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        btn: QPushButton = watched
        if btn:
            if event.type() == QEvent.Type.EnabledChange and not btn.isEnabled():
                btn.setEnabled(True)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.base_dir = (
                    self.directory().absolutePath()
                )  # Save current dir, after changing fileMode it could be changed
                if not self.exist:
                    self.setFileMode(QFileDialog.FileMode.AnyFile)

        return QWidget.eventFilter(self, watched, event)

    @Slot()
    def openClicked(self):
        self.selected_path = ""
        for model_index in self.tree_view.selectionModel().selectedIndexes():
            if model_index.column() == 0:
                self.selected_path = (
                    self.base_dir + QDir.separator() + str(model_index.data())
                )
                self.selected_path.replace("/", QDir.separator())
                break

        if not self.selected_path and not self.exist:
            self.selected_path = (
                self.base_dir
                + QDir.separator()
                + self.findChild(QLineEdit, "fileNameEdit").text()
            )
            self.selected_path.replace("/", QDir.separator())
            QDialog.accept(self)
        elif (
            self.selected_path
        ):  # Don't close if the user selected an invalid file/folder
            QDialog.accept(self)
