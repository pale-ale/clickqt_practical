from abc import ABC
from PySide6.QtWidgets import QLineEdit, QComboBox, QDateTimeEdit, QCheckBox


class CustomWidget(ABC):
    def __init__(self, widget_type) -> None:
        self.widget_type = widget_type

        self.supported_widgets = {
            QLineEdit: {
                "setter": self.widget_type.setText,
                "getter": self.widget_type.text,
            },
            QComboBox: {
                "setter": self.widget_type.setCurrentIndex,
                "getter": self.widget_type.currentIndex,
            },
            QDateTimeEdit: {
                "setter": self.widget_type.setDateTime,
                "getter": self.widget_type.dateTime,
            },
            QCheckBox: {
                "setter": self.widget_type.setChecked,
                "getter": self.widget_type.isChecked,
            },
        }
