from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._WriteStructuralFeatureAction import WriteStructuralFeatureAction

class AddStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """UML metaclass AddStructuralFeatureValueAction."""
    __spec__ = SPECIFICATIONS['AddStructuralFeatureValueAction']
    insertAt: InputPin | None
    isReplaceAll: bool | None
