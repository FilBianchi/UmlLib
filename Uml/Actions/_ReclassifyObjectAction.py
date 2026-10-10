from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._Action import Action

class ReclassifyObjectAction(Action):
    """UML metaclass ReclassifyObjectAction."""
    __spec__ = SPECIFICATIONS['ReclassifyObjectAction']
    isReplaceAll: bool | None
    newClassifier: list[Classifier]
    object: InputPin | None
    oldClassifier: list[Classifier]
