from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class UnmarshallAction(Action):
    """UML metaclass UnmarshallAction."""
    __spec__ = SPECIFICATIONS['UnmarshallAction']
    object: InputPin | None
    result: list[OutputPin]
    unmarshallType: Classifier | None
