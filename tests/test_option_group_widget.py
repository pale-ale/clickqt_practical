import pytest
import click
from click_option_group import OptionGroup
from click_option_group._core import _GroupTitleFakeOption
from PySide6.QtWidgets import QWidget
from clickqt.core.control import Control
from clickqt.core.core import qtgui_from_click
from tests.testutils import ClickAttrs


def determine_relevant_widgets(control_instance: Control):
    content_widget = control_instance.gui.widgets_container.widget()
    child_widgets = content_widget.findChildren(QWidget)
    widgets_with_name = []

    for index, widget in enumerate(child_widgets):
        if widget.objectName() != "":
            widgets_with_name.append((index, widget.objectName()))
    return widgets_with_name


def determine_widgets_for_comp(widgets: list, cmd, p_name2: str = None):
    widgets_to_compare = []
    param_names = []
    if p_name2 is not None:
        param_names.append(p_name2)
    params = cmd.params
    for param in params:
        if isinstance(param, _GroupTitleFakeOption):
            param_names.append(param.name)
    for widget in widgets:
        if widget[1] == param_names[0] or widget[1] == param_names[1]:
            widgets_to_compare.append(widget)

    return widgets_to_compare


@pytest.mark.parametrize(
    ("click_attrs"),
    [
        (ClickAttrs.intfield()),
        (ClickAttrs.passwordfield()),
        (ClickAttrs.checkbox()),
        (ClickAttrs.datetime()),
        (ClickAttrs.checkable_combobox(choices=["A", "B"])),
        (ClickAttrs.combobox(choices=["A", "B"])),
        (ClickAttrs.filefield()),
        (ClickAttrs.floatrange()),
        (ClickAttrs.intrange()),
        (ClickAttrs.multi_value_widget(nargs=2)),
        (ClickAttrs.nvalue_widget()),
        (ClickAttrs.passwordfield()),
        (ClickAttrs.tuple_widget(types=[str, str])),
        (ClickAttrs.realfield()),
        (ClickAttrs.uuid()),
        (ClickAttrs.textfield()),
    ],
)
def test_option_group_ordering(click_attrs: dict):
    group = OptionGroup("Server configuration")

    @click.command("main")
    @group.option("--opt1")
    @group.option("--opt2")
    def cli(**params):
        print(params)

    cmd = cli
    parameter = click.Option(param_decls=["--p"], **click_attrs)
    cmd.params.append(parameter)
    control = qtgui_from_click(cmd)

    widgets = determine_relevant_widgets(control)
    # check if all the widgets are correctly ordered in the hierarchy
    for i, widget in enumerate(widgets):
        if i < len(widgets) - 1:
            assert widget[0] < widgets[i + 1][0]
    comp_widgets = determine_widgets_for_comp(widgets, cmd, parameter.name)
    assert comp_widgets[0][0] < comp_widgets[1][0]


def test_option_group_fail():
    """This test will fail if you comment one of the options out"""
    group = OptionGroup("Group 1")

    @click.command("main")
    @group.option("--opt1")
    @group.option("--opt2")
    def cli(**params):
        print(params)

    cmd = cli
    control = qtgui_from_click(cmd)
    widgets = determine_relevant_widgets(control)
    assert len(widgets) == 3


def test_option_group_simple_ordering():
    group = OptionGroup("Group 1")
    group2 = OptionGroup("Group 2")

    @click.command("main")
    @group.option("--opt1")
    @group.option("--opt2")
    @group2.option("--op1")
    @group2.option("--op2")
    def cli(**params):
        print(params)

    cmd = cli
    control = qtgui_from_click(cmd)
    widgets = determine_relevant_widgets(control)
    comp_widgets = determine_widgets_for_comp(widgets, cmd)
    assert comp_widgets[0][0] < comp_widgets[1][0]
