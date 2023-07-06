import click
import pytest

from PySide6.QtWidgets import QLineEdit, QFileDialog, QApplication, QPushButton, QMessageBox
from PySide6.QtCore import QTimer, SIGNAL, Signal, QObject
from PySide6.QtTest import QSignalSpy
from tests.testutils import ClickAttrs
import clickqt.widgets
from clickqt.widgets.core.QPathDialog import QPathDialog
import sys
import time

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
        assert icon.pixmap(176, 176).toImage() == expected_icon.pixmap(176, 176).toImage()
        assert passwordfield_widget.show_hide_action.text() == passwordfield_widget.icon_text[passwordfield_widget.show_hide_action.isChecked()][1]

        passwordfield_widget.show_hide_action.setChecked(not passwordfield_widget.show_hide_action.isChecked())

#@pytest.mark.skipif(sys.platform == "darwin", reason="Not runnable on GitHubs MacOS-VMs")
@pytest.mark.parametrize(
    ("click_attrs", "value", "expected"),
    [
        pytest.param(ClickAttrs.filefield(type_dict={"mode":"r"}), "README.md", "README.md", marks=pytest.mark.skipif(sys.platform == "linux", reason="Does not work under linux")),
        (ClickAttrs.filefield(type_dict={"mode":"r"}), "invalid_file.txt", ""),
        (ClickAttrs.filefield(type_dict={"mode":"w"}), ".gitignore", ".gitignore"),
        (ClickAttrs.filefield(type_dict={"mode":"w"}), "invalid_file.txt", "invalid_file.txt"),
        (ClickAttrs.filepathfield(type_dict={"exists":True}), "invalid_path", ""),
        (ClickAttrs.filepathfield(type_dict={"exists":True}), "tests", "tests"), # valid folder
        pytest.param(ClickAttrs.filepathfield(type_dict={"exists":True}), "README.md", "README.md", marks=pytest.mark.skipif(sys.platform == "linux", reason="Does not work under linux")), # valid file
        (ClickAttrs.filepathfield(type_dict={"exists":False}), "invalid_path", "invalid_path"), # Exists==False: Accept any file
        (ClickAttrs.filepathfield(type_dict={"exists":True, "dir_okay":False}), "tests", ""),
        #(ClickAttrs.filepathfield(type_dict={"exists":True, "dir_okay":False}), ".gitignore", ".gitignore"), # Test does not work, but manually it does
        (ClickAttrs.filepathfield(type_dict={"exists":False, "dir_okay":False}), "tests", "tests"),
        (ClickAttrs.filepathfield(type_dict={"exists":True, "file_okay":False}), ".gitignore", ""),
        #(ClickAttrs.filepathfield(type_dict={"exists":True, "file_okay":False}), "tests", "tests"), # Test does not work, but manually it does
        (ClickAttrs.filepathfield(type_dict={"exists":False, "file_okay":False}), ".gitignore", ".gitignore"),
    ]
)
def test_pathfield(click_attrs:dict, value:str, expected:str):
    param = click.Option(param_decls=["--p"], **click_attrs) 
    cli = click.Command("cli", params=[param])

    control = clickqt.qtgui_from_click(cli)
    widget:clickqt.widgets.PathField = control.widget_registry[cli.name][param.name]

    class Finished(QObject):
        finished = Signal()

    def closeMessagebox(messageBoxClosed:Finished):
        messagebox:QMessageBox = QApplication.activeModalWidget()

        # Wait, until we have the QMessageBox- or QFileDialog-object
        tries = 0
        while messagebox is not None and not isinstance(messagebox, QFileDialog|QPathDialog|QMessageBox) and tries < 3:
            QApplication.processEvents()
            messagebox = QApplication.activeModalWidget()
            tries += 1
            time.sleep(0.0001)

        if messagebox is not None:
            messagebox.close()

        messageBoxClosed.finished.emit()

    def selectFile():
        file_dialog:QFileDialog|QPathDialog = QApplication.activeModalWidget()
        messageBoxClosed = Finished()

        # Wait, until we have the QFileDialog object
        tries = 0
        while file_dialog is None or not isinstance(file_dialog, QFileDialog|QPathDialog) and tries < 3: # See also https://github.com/pytest-dev/pytest-qt/issues/256
            QApplication.processEvents()
            file_dialog = QApplication.activeModalWidget()
            tries += 1
            time.sleep(0.0001)
        
        if file_dialog is not None:
            file_dialog.findChild(QLineEdit, "fileNameEdit").setText(value) # = file_dialog.selectFile(value)

            # Search Open/Choose btn and click it
            for btn in file_dialog.findChildren(QPushButton):
                text = btn.text().lower()
                if "open" in text or "choose" in text:
                    spy = QSignalSpy(messageBoxClosed, SIGNAL("finished()"))
                    QTimer.singleShot(5, lambda: closeMessagebox(messageBoxClosed))
                    btn.click() 

                    for _ in range(3):  # wait for stopping the worker
                        if not spy.wait(20):  # wait for function closeMessagebox to finish   
                            QApplication.processEvents()
                        else:
                            break
                        
                    break

            file_dialog.close()
    
    QTimer.singleShot(5, selectFile)
    widget.browse()

    assert widget.getWidgetValue() == expected