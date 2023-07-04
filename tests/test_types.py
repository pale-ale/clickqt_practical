import click
import pytest

from PySide6.QtWidgets import QLineEdit
from tests.testutils import ClickAttrs
import clickqt.widgets

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
        (ClickAttrs.intrange(), clickqt.widgets.IntField), 
        (ClickAttrs.floatrange(), clickqt.widgets.RealField), 
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
    gui = control.gui
    
    assert type(gui.create_widget(param.type, param, widgetsource=gui.create_widget, com=cli)) is expected_clickqt_type , "directly" # Perfect type match
    assert type(control.widget_registry[cli.name][param.name]) is expected_clickqt_type, "clickqt" # Perfect type match

@pytest.mark.parametrize(
    ("click_attrs_list", "expected_clickqt_type_list"),
    [
        ([ClickAttrs.checkbox(), ClickAttrs.intfield(), ClickAttrs.realfield(), ClickAttrs.passwordfield()], 
         [clickqt.widgets.CheckBox, clickqt.widgets.IntField, clickqt.widgets.RealField, clickqt.widgets.PasswordField]),
        ([ClickAttrs.filefield(), ClickAttrs.filepathfield(), ClickAttrs.tuple_widget(types=(click.types.Path(),int))], 
         [clickqt.widgets.FileField, clickqt.widgets.FilePathField, clickqt.widgets.TupleWidget]),
        ([ClickAttrs.datetime(), ClickAttrs.combobox(choices=["a"]), ClickAttrs.nvalue_widget(), ClickAttrs.multi_value_widget(nargs=2)], 
         [clickqt.widgets.DateTimeEdit, clickqt.widgets.ComboBox, clickqt.widgets.NValueWidget, clickqt.widgets.MultiValueWidget]),
    ]
)
def test_type_assignment_multiple_options(click_attrs_list:list[dict], expected_clickqt_type_list:list[clickqt.widgets.BaseWidget]):
    params = []

    for i, click_attrs in enumerate(click_attrs_list):
        params.append(click.Option(param_decls=["--test" + str(i)], **click_attrs))

    cli = click.Command("cli", params=params)

    control = clickqt.qtgui_from_click(cli)
    for i, v in enumerate(control.widget_registry[cli.name].values()):
        assert type(v) is expected_clickqt_type_list[i] # Perfect type match

@pytest.mark.parametrize(
    ("click_attrs_list", "expected_clickqt_type_list"),
    [
        ([[ClickAttrs.checkbox(), ClickAttrs.intfield()], [ClickAttrs.realfield(), ClickAttrs.passwordfield()]], 
         [[clickqt.widgets.CheckBox, clickqt.widgets.IntField], [clickqt.widgets.RealField, clickqt.widgets.PasswordField]]),
        ([[ClickAttrs.filefield(), ClickAttrs.filepathfield()], [ClickAttrs.tuple_widget(types=(click.types.Path(),int))]], 
         [[clickqt.widgets.FileField, clickqt.widgets.FilePathField], [clickqt.widgets.TupleWidget]]),
        ([[ClickAttrs.datetime(), ClickAttrs.combobox(choices=["a"]), ClickAttrs.nvalue_widget()], [ClickAttrs.multi_value_widget(nargs=2)]], 
         [[clickqt.widgets.DateTimeEdit, clickqt.widgets.ComboBox, clickqt.widgets.NValueWidget], [clickqt.widgets.MultiValueWidget]]),
    ]
)
def test_type_assignment_multiple_commands(click_attrs_list:list[list[dict]], expected_clickqt_type_list:list[list[clickqt.widgets.BaseWidget]]):
    clis = []

    for i, cli_params in enumerate(click_attrs_list):
        params = []

        for j, click_attrs in enumerate(cli_params):
            params.append(click.Option(param_decls=["--test" + str(j)], **click_attrs))

        clis.append(click.Command("cli" + str(i), params=params))

    group = click.Group("group", commands=clis)

    control = clickqt.qtgui_from_click(group)
    for i, cli_name in enumerate(control.widget_registry.keys()):
        for j, v in enumerate(control.widget_registry[cli_name].values()):
            assert type(v) is expected_clickqt_type_list[i][j] # Perfect type match

def test_passwordfield_showPassword():
    param = click.Option(param_decls=["--p"], **ClickAttrs.passwordfield()) 
    cli = click.Command("cli", params=[param])
    
    control = clickqt.qtgui_from_click(cli)
    passwordfield_widget:clickqt.widgets.PasswordField = control.widget_registry[cli.name][param.name]

    for _ in range(3):
        assert passwordfield_widget.widget.echoMode() == QLineEdit.EchoMode.Normal if passwordfield_widget.show_hide_action.isChecked() else QLineEdit.EchoMode.Password
        # QIcons cannot be compared, but QImages can
        icon = passwordfield_widget.show_hide_action.icon()
        expected_icon = passwordfield_widget.icon_text[passwordfield_widget.show_hide_action.isChecked()][0]
        assert icon.pixmap(icon.availableSizes()[0]).toImage() == expected_icon.pixmap(expected_icon.availableSizes()[0]).toImage()
        assert passwordfield_widget.show_hide_action.text() == passwordfield_widget.icon_text[passwordfield_widget.show_hide_action.isChecked()][1]

        passwordfield_widget.show_hide_action.setChecked(not passwordfield_widget.show_hide_action.isChecked())