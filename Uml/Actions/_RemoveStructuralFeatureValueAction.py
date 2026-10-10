from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._WriteStructuralFeatureAction import WriteStructuralFeatureAction

class RemoveStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """UML metaclass RemoveStructuralFeatureValueAction."""
    __spec__ = SPECIFICATIONS['RemoveStructuralFeatureValueAction']
    isRemoveDuplicates: bool | None
    removeAt: InputPin | None
