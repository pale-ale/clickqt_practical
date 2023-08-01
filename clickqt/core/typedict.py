import click
from clickqt.widgets.checkbox import CheckBox
from clickqt.widgets.textfield import TextField
from clickqt.widgets.numericfields import IntField, RealField
from clickqt.widgets.combobox import ComboBox
from clickqt.widgets.datetimeedit import DateTimeEdit
from clickqt.widgets.tuplewidget import TupleWidget
from clickqt.widgets.filepathfield import FilePathField
from clickqt.widgets.filefield import FileField

typedict = {
    click.types.BoolParamType: CheckBox,
    click.types.IntParamType: IntField,
    click.types.FloatParamType: RealField,
    click.types.StringParamType: TextField,
    click.types.UUIDParameterType: TextField,
    click.types.UnprocessedParamType: TextField,
    click.types.DateTime: DateTimeEdit,
    click.types.Tuple: TupleWidget,
    click.types.Choice: ComboBox,
    click.types.Path: FilePathField,
    click.types.File: FileField,
}
