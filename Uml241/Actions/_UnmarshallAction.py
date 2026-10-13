from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class UnmarshallAction(Action):
    """UML metaclass UnmarshallAction."""
    __spec__ = SPECIFICATIONS['UnmarshallAction']
    object: InputPin | None
    result: list[OutputPin]
    unmarshallType: Classifier | None
