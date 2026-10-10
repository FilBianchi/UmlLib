from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship
from ..CommonStructure._PackageableElement import PackageableElement

class Dependency(DirectedRelationship, PackageableElement):
    """UML metaclass Dependency."""
    __spec__ = SPECIFICATIONS['Dependency']
    client: list[NamedElement]
    supplier: list[NamedElement]
