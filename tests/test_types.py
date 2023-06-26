import click
import pytest

from tests.testutils import ClickAttrs
import clickqt.widgets
from typing import Any

@pytest.mark.parametrize(
    ("click_attrs", "expected_clickqt_type"),
    [
        (ClickAttrs.checkbox(), clickqt.widgets.CheckBox),
        (ClickAttrs.messagebox(prompt="Test"), clickqt.widgets.MessageBox),  
        (ClickAttrs.intfield(), clickqt.widgets.IntField), 
        (ClickAttrs.realfield(), clickqt.widgets.RealField), 
        (ClickAttrs.confirmation_widget(), clickqt.widgets.ConfirmationWidget),
        (ClickAttrs.textfield(), clickqt.widgets.TextField),
        (ClickAttrs.passwordfield(), clickqt.widgets.PasswordField),
        (ClickAttrs.datetime(), clickqt.widgets.DateTimeEdit),
        (ClickAttrs.uuid(), clickqt.widgets.TextField), 
        (ClickAttrs.unprocessed(), clickqt.widgets.TextField), 
        (ClickAttrs.combobox(choices=["a"]), clickqt.widgets.ComboBox), 
        (ClickAttrs.checkable_combobox(choices=["a"]), clickqt.widgets.CheckableComboBox), 
        (ClickAttrs.filefield(), clickqt.widgets.FileField), 
        (ClickAttrs.filepathfield(), clickqt.widgets.FilePathField), 
        (ClickAttrs.nvalue_widget(), clickqt.widgets.NValueWidget),
        (ClickAttrs.tuple_widget(types=(click.types.Path(),int)), clickqt.widgets.TupleWidget),
        (ClickAttrs.multi_value_widget(nargs=2), clickqt.widgets.MultiValueWidget),  
    ]
)
def test_type_assignment(click_attrs:dict, expected_clickqt_type:clickqt.widgets.BaseWidget):
    param = click.Option(param_decls=["--test"], **click_attrs)
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    assert type(control.widget_registry[cli.name][param.name]) is expected_clickqt_type, "clickqt"
