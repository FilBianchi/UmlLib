from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship
from ..CommonStructure._PackageableElement import PackageableElement

class Dependency(DirectedRelationship, PackageableElement):
    """UML metaclass Dependency."""
    __spec__ = SPECIFICATIONS['Dependency']
    client: list[NamedElement]
    supplier: list[NamedElement]
