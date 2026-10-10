from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReadIsClassifiedObjectAction(Action):
    """UML metaclass ReadIsClassifiedObjectAction."""
    __spec__ = SPECIFICATIONS['ReadIsClassifiedObjectAction']
    classifier: Classifier | None
    isDirect: bool | None
    object: InputPin | None
    result: OutputPin | None
