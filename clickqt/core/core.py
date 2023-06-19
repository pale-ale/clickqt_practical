from clickqt.core.control import Control
from PySide6.QtWidgets import QApplication

def qtgui_from_click(cmd):
    # Testing: The testing suite creates a QApplication instance
    if QApplication.instance() is None:
        app = QApplication([])
        app.setApplicationName("GUI for CLI")
        app.setStyleSheet("""QToolTip { 
                        background-color: #182035; 
                        color: white; 
                        border: white solid 1px
                        }""")

    return Control(cmd)
