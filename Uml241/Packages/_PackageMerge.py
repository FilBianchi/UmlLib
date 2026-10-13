from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class PackageMerge(DirectedRelationship):
    """UML metaclass PackageMerge."""
    __spec__ = SPECIFICATIONS['PackageMerge']
    mergedPackage: Package | None
    receivingPackage: Package | None
