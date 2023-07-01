from PySide6.QtWidgets import QLineEdit
from clickqt.widgets.textfield import PathField
from click import Parameter, Path, ParamType

class FilePathField(PathField):
    widget_type = QLineEdit

    def __init__(self, otype:ParamType, param:Parameter, *args, **kwargs):
        super().__init__(otype, param, *args, **kwargs)

        assert isinstance(otype, Path), f"'otype' must be of type '{Path}', but is '{type(otype)}'."
        
        self.file_type |= PathField.FileType.File if otype.file_okay else self.file_type
        self.file_type |= PathField.FileType.Directory if otype.dir_okay else self.file_type

        if self.file_type == PathField.FileType.Unknown:
            raise ValueError(f"Neither 'file_okay' nor 'dir_okay' in argument '{self.widget_name}' is set")
