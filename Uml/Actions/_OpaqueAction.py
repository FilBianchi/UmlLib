from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class OpaqueAction(Action):
    """UML metaclass OpaqueAction."""
    __spec__ = SPECIFICATIONS['OpaqueAction']
    body: list[str]
    inputValue: list[InputPin]
    language: list[str]
    outputValue: list[OutputPin]
