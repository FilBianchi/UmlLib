from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._MultiplicityElement import MultiplicityElement
from ..CommonStructure._TypedElement import TypedElement
from ..Classification._Feature import Feature

class StructuralFeature(MultiplicityElement, TypedElement, Feature):
    """UML metaclass StructuralFeature."""
    __spec__ = SPECIFICATIONS['StructuralFeature']
    isReadOnly: bool | None
