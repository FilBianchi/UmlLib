from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class CreateObjectAction(Action):
    """UML metaclass CreateObjectAction."""
    __spec__ = SPECIFICATIONS['CreateObjectAction']
    classifier: Classifier | None
    result: OutputPin | None
