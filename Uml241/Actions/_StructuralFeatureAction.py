from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class StructuralFeatureAction(Action):
    """UML metaclass StructuralFeatureAction."""
    __spec__ = SPECIFICATIONS['StructuralFeatureAction']
    object: InputPin | None
    structuralFeature: StructuralFeature | None
