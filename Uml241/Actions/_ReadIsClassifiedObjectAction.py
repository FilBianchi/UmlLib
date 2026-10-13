from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class ReadIsClassifiedObjectAction(Action):
    """UML metaclass ReadIsClassifiedObjectAction."""
    __spec__ = SPECIFICATIONS['ReadIsClassifiedObjectAction']
    classifier: Classifier | None
    isDirect: bool | None
    object: InputPin | None
    result: OutputPin | None
