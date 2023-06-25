from PySide6.QtWidgets import QApplication

app = QApplication.instance() if QApplication.instance() is not None else QApplication([])