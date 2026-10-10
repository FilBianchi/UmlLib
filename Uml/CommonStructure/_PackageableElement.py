from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._ParameterableElement import ParameterableElement
from ..CommonStructure._NamedElement import NamedElement

class PackageableElement(ParameterableElement, NamedElement):
    """UML metaclass PackageableElement."""
    __spec__ = SPECIFICATIONS['PackageableElement']
    visibility: VisibilityKind | None
