from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from clickqt.core.control import Control


def qtgui_from_click(cmd, **kwargs):
    """This function is used to generate the GUI for a given command. It takes a click command as its argument and returns a Control object
    that contains the GUI, execution logic, and the generated widgets used for the parameters of the command.

    :param cmd: The click.Command-object to create a GUI from
    :param kwargs: Additional GUI options. Currently supported arguments are:
                  '*window_icon*': Path to an icon, changes the icon of the application
                  '*application_name*': Name of the application

    :return: The control-object that contains the GUI
    """
    if QApplication.instance() is None:
        # Testing: The testing suite creates a QApplication instance
        app = QApplication([])
        app.setWindowIcon(QIcon(kwargs.get("window_icon")))
        app.setApplicationName(kwargs.get("application_name"))

    return Control(cmd)
