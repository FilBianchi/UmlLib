from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._WriteStructuralFeatureAction import WriteStructuralFeatureAction

class RemoveStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """UML metaclass RemoveStructuralFeatureValueAction."""
    __spec__ = SPECIFICATIONS['RemoveStructuralFeatureValueAction']
    isRemoveDuplicates: bool | None
    removeAt: InputPin | None
