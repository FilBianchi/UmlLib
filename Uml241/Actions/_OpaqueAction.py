from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class OpaqueAction(Action):
    """UML metaclass OpaqueAction."""
    __spec__ = SPECIFICATIONS['OpaqueAction']
    body: list[str]
    inputValue: list[InputPin]
    language: list[str]
    outputValue: list[OutputPin]
