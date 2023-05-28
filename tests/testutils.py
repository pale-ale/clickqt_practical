from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPoint
from pytestqt.qtbot import QtBot
import PySide6.QtCore as QtCore

def keystrokes(target:QWidget, bot:QtBot, chars:str):
  for char in chars:
    if key := getattr(QtCore.Qt.Key, f"Key_{char}", None):
      bot.keyClick(target, key)
    else:
      raise ValueError(f"'{char}' is not a valid key name for qtest")