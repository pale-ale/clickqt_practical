import click
from click.types import ParamType, BoolParamType, StringParamType, IntParamType, Choice
from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QSpinBox, QComboBox
from .checkableComboBox import CheckableComboBox
from typing import Callable

Parameter = click.Argument|click.Option

class PostProcessor():
  def __init__(self) -> None:
    self.defaults:dict[ParamType(), Callable[[Parameter]]] = {}
    self.applicators:dict[ParamType(), Callable[[QWidget, Parameter]]] = {
      BoolParamType:self.process_bool,
      StringParamType:self.process_str,
      IntParamType:self.process_int,
      Choice: self.process_choice
    }
  
  def post_process(self, w:QWidget, p:Parameter):
    for paramtype, processfunc in self.applicators.items():
      if isinstance(p.type, paramtype):
        print(f"Processing {p.type}...")
        processfunc(w, p)

  @staticmethod
  def default_fallback(p:Parameter):
    return p.default() if callable(p.default) else p.default
  
  def _get_default(self, p:Parameter):
    return self.defaults[p.type]() if p.type in self.defaults else __class__.default_fallback(p)

  def process_bool(self, widget:QCheckBox, p:Parameter):
    widget.setChecked(self._get_default(p))

  def process_str(self, widget:QLineEdit, p:Parameter):
    widget.setText(self._get_default(p))
    if hasattr(p, "hide_input"):
      widget.setEchoMode(QLineEdit.EchoMode.Password)
  
  def process_int(self, widget:QSpinBox, p:Parameter):
    widget.setValue(self._get_default(p))

  def process_choice(self, widget:QComboBox|CheckableComboBox, p:Parameter):
    widget.addItems(p.to_info_dict()["type"]["choices"])