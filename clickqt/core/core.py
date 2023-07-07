from clickqt.core.control import Control
from PySide6.QtWidgets import QApplication

def qtgui_from_click(cmd, is_ep, ep_or_eppath=None):
    # Testing: The testing suite creates a QApplication instance
    """ 
        This function is used to generate the GUI for the given command. It takes a predefined click command as its argument and returns a Control object
        that contains the GUI and the logic behind the execution and the generated widgets for used for the parameters of the command.
    """
    if QApplication.instance() is None:
        app = QApplication([])
        app.setApplicationName("GUI for CLI")
        app.setStyleSheet("""QToolTip { 
                        background-color: #182035; 
                        color: white; 
                        border: white solid 1px
                        }""")
    return Control(cmd, is_ep, ep_or_eppath)
