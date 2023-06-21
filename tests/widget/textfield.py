import click
import clickqt
from clickqt.widgets.textfield import TextField
import random
import string
import os

def test_gui_textfield():
    expected:str = "test"

    @click.command()
    @click.option("--message", default=expected)
    def dist(message):
        assert isinstance(message, str)
        assert message == expected

    control = clickqt.qtgui_from_click(dist)
    run_button = control.gui.run_button
    textfield_widget = control.widget_registry[dist.name][dist.params[0].name]
    assert isinstance(textfield_widget, TextField)
    # Check if default value was set correctly
    run_button.click() 

    for _ in range(5):
        expected = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        textfield_widget.setValue(expected)
        run_button.click() 

    # Wrong type does not change the widget value
    textfield_widget.setValue(123)
    run_button.click() 

def test_gui_textfield_envvar():
    expected:str = None
    temp_envvars = ["TMPDIR", "TEMP", "TMP", "SHELL"] # OS dependent
    for envvar in temp_envvars:
        if (path := os.environ.get(envvar)):
            expected = path
            break

    @click.command()
    @click.option("--message", envvar=temp_envvars)
    def dist(message):
        assert isinstance(message, str)
        assert message == expected

    control = clickqt.qtgui_from_click(dist)
    run_button = control.gui.run_button
    textfield_widget = control.widget_registry[dist.name][dist.params[0].name]
    assert isinstance(textfield_widget, TextField)
    # Check if envvar value was set correctly
    run_button.click() 
