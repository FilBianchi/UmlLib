from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._StructuralFeatureAction import StructuralFeatureAction

class ClearStructuralFeatureAction(StructuralFeatureAction):
    """UML metaclass ClearStructuralFeatureAction."""
    __spec__ = SPECIFICATIONS['ClearStructuralFeatureAction']
    result: OutputPin | None
