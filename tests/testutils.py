import click
from typing import Sequence, Type

def raise_(ex:Exception):
    raise ex

class ClickAttrs():
    @staticmethod
    def unprocessed(**attrs_dict) -> dict:
        return {"type":click.types.UNPROCESSED, **attrs_dict}
    
    @staticmethod
    def messagebox(prompt:str, **attrs_dict) -> dict:
        return {"type":click.types.BOOL, "is_flag":True, "prompt":prompt, **attrs_dict}
    
    @staticmethod
    def intfield(**attrs_dict) -> dict:
        return {"type":click.types.INT, **attrs_dict}
    
    @staticmethod
    def passwordfield(**attrs_dict) -> dict:
        return {"type":click.types.STRING, "hide_input":True, **attrs_dict}
    
    @staticmethod
    def realfield(**attrs_dict) -> dict:
        return {"type":click.types.FLOAT, **attrs_dict}
    
    @staticmethod
    def intrange(min:int|None=None, max:int|None=None, min_open:bool=False, max_open:bool=False, clamp:bool=False, **attrs_dict) -> dict:
        return {"type":click.IntRange(min=min, max=max, min_open=min_open, max_open=max_open, clamp=clamp), **attrs_dict}
    
    @staticmethod
    def floatrange(min:int|None=None, max:int|None=None, min_open:bool=False, max_open:bool=False, clamp:bool=False, **attrs_dict) -> dict:
        return {"type":click.FloatRange(min=min, max=max, min_open=min_open, max_open=max_open, clamp=clamp), **attrs_dict}
    
    @staticmethod
    def confirmation_widget(**attrs_dict) -> dict:
        return {"confirmation_prompt":True, **attrs_dict}
    
    @staticmethod
    def checkbox(**attrs_dict) -> dict:
        return {"type":click.types.BOOL, **attrs_dict}

    @staticmethod
    def combobox(choices:Sequence[str], case_sensitive:bool=True, **attrs_dict) -> dict:
        return {"type":click.types.Choice(choices=choices, case_sensitive=case_sensitive), **attrs_dict}

    @staticmethod
    def checkable_combobox(choices:Sequence[str], case_sensitive:bool=True, **attrs_dict) -> dict:
        return {"type":click.types.Choice(choices=choices, case_sensitive=case_sensitive), "multiple":True, **attrs_dict}
    
    @staticmethod
    def filefield(type_dict:dict={}, **attrs_dict) -> dict:
        return {"type":click.types.File(**type_dict), **attrs_dict}
    
    @staticmethod
    def filepathfield(type_dict:dict={}, **attrs_dict) -> dict:
        return {"type":click.types.Path(**type_dict), **attrs_dict}
    
    @staticmethod
    def datetime(formats:Sequence[str]|None=None, **attrs_dict) -> dict:
        return {"type":click.types.DateTime(formats), **attrs_dict}
    
    @staticmethod
    def tuple_widget(types:Sequence[Type|click.ParamType], **attrs_dict) -> dict:
        return {"type":click.types.Tuple(types), **attrs_dict}
    
    @staticmethod
    def multi_value_widget(nargs:int, **attrs_dict) -> dict:
        assert nargs > 1
        return {"nargs":nargs, **attrs_dict}
    
    @staticmethod
    def nvalue_widget(**attrs_dict) -> dict:
        assert attrs_dict.get("type") is None or attrs_dict.get("type") is not bool
        return {"multiple":True, **attrs_dict}
    
    @staticmethod
    def uuid(**attrs_dict) -> dict:
        return {"type":click.types.UUID, **attrs_dict}
    
    @staticmethod
    def textfield(**attrs_dict) -> dict:
        return {"type":click.types.STRING, **attrs_dict}
