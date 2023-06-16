from PySide6.QtWidgets import QLineEdit
from clickqt.widgets.base_widget import PathField
from click import Parameter, Path

class FilePathField(PathField):
    widget_type = QLineEdit

    def __init__(self, param:Parameter, *args, **kwargs):
        super().__init__(param, *args, **kwargs)

        if not isinstance(param.type, Path):
            raise TypeError("'param' must be of type 'Path'.")
        self.file_type |= PathField.FileType.File if param.type.file_okay else self.file_type
        self.file_type |= PathField.FileType.Directory if param.type.dir_okay else self.file_type

        if self.file_type == PathField.FileType.Unknown:
            raise ValueError(f"Neither 'file_okay' nor 'dir_okay' in argument '{self.widget_name}' is set")
        
    def getWidgetValue(self) -> str:
        return self.widget.text()
   
    def getWidgetValueToString(self) -> str:
        return self.getWidgetValue()