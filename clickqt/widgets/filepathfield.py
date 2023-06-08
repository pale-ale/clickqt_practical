from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QFile
from clickqt.widgets.base_widget import PathField

class FilePathField(PathField):
    widget_type = QLineEdit

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.file_type |= PathField.FileType.File if options["type"]["file_okay"] else self.file_type
        self.file_type |= PathField.FileType.Directory if options["type"]["dir_okay"] else self.file_type

        if self.file_type == PathField.FileType.Unknown:
            raise ValueError(f"Neither 'file_okay' nor 'dir_okay' in argument '{self.widget_name}' is set")
        
    def getWidgetValue(self) -> str:
        return self.widget.text()
   