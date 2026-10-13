from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._ParameterableElement import ParameterableElement
from ..CommonStructure._NamedElement import NamedElement

class PackageableElement(ParameterableElement, NamedElement):
    """UML metaclass PackageableElement."""
    __spec__ = SPECIFICATIONS['PackageableElement']
    visibility: VisibilityKind | None
