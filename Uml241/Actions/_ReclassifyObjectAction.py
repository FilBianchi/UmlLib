from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class ReclassifyObjectAction(Action):
    """UML metaclass ReclassifyObjectAction."""
    __spec__ = SPECIFICATIONS['ReclassifyObjectAction']
    isReplaceAll: bool | None
    newClassifier: list[Classifier]
    object: InputPin | None
    oldClassifier: list[Classifier]
