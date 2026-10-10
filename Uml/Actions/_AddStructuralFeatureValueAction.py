from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._WriteStructuralFeatureAction import WriteStructuralFeatureAction

class AddStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """UML metaclass AddStructuralFeatureValueAction."""
    __spec__ = SPECIFICATIONS['AddStructuralFeatureValueAction']
    insertAt: InputPin | None
    isReplaceAll: bool | None
