from PySide6.QtWidgets import QLineEdit
from clickqt.widgets.textfield import PathField
from click import Parameter, Path, ParamType

class FilePathField(PathField):
    widget_type = QLineEdit

    def __init__(self, otype:ParamType, param:Parameter, **kwargs):
        super().__init__(otype, param, **kwargs)

        assert isinstance(otype, Path), f"'otype' must be of type '{Path}', but is '{type(otype)}'."
        
        self.file_type |= PathField.FileType.File if otype.file_okay else self.file_type
        self.file_type |= PathField.FileType.Directory if otype.dir_okay else self.file_type

        assert self.file_type != PathField.FileType.Unknown, f"Neither 'file_okay' nor 'dir_okay' in option '{self.widget_name}' is set"
