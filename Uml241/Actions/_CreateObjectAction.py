from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class CreateObjectAction(Action):
    """UML metaclass CreateObjectAction."""
    __spec__ = SPECIFICATIONS['CreateObjectAction']
    classifier: Classifier | None
    result: OutputPin | None
