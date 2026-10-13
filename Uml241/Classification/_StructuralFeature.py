from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._MultiplicityElement import MultiplicityElement
from ..CommonStructure._TypedElement import TypedElement
from ..Classification._Feature import Feature

class StructuralFeature(MultiplicityElement, TypedElement, Feature):
    """UML metaclass StructuralFeature."""
    __spec__ = SPECIFICATIONS['StructuralFeature']
    isReadOnly: bool | None
