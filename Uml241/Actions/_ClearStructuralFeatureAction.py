from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._StructuralFeatureAction import StructuralFeatureAction

class ClearStructuralFeatureAction(StructuralFeatureAction):
    """UML metaclass ClearStructuralFeatureAction."""
    __spec__ = SPECIFICATIONS['ClearStructuralFeatureAction']
    result: OutputPin | None
