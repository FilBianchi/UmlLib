from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReadExtentAction(Action):
    """UML metaclass ReadExtentAction."""
    __spec__ = SPECIFICATIONS['ReadExtentAction']
    classifier: Classifier | None
    result: OutputPin | None
