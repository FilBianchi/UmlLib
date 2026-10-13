from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._StructuralFeatureAction import StructuralFeatureAction

class WriteStructuralFeatureAction(StructuralFeatureAction):
    """UML metaclass WriteStructuralFeatureAction."""
    __spec__ = SPECIFICATIONS['WriteStructuralFeatureAction']
    result: OutputPin | None
    value: InputPin | None
