from clickqt.core.control import Control
from PySide6.QtWidgets import QApplication

def qtgui_from_click(cmd):
    """ 
        This function is used to generate the GUI for a given command. It takes a click command as its argument and returns a Control object
        that contains the GUI, execution logic, and the generated widgets used for the parameters of the command.
    """
    if QApplication.instance() is None: # Testing: The testing suite creates a QApplication instance
        app = QApplication([])
        app.setApplicationName("GUI for CLI")
        app.setStyleSheet("""QToolTip { 
                        background-color: #182035; 
                        color: white; 
                        border: white solid 1px
                        }""")
    return Control(cmd)
