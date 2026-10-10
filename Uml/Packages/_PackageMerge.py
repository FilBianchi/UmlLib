from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._DirectedRelationship import DirectedRelationship

class PackageMerge(DirectedRelationship):
    """UML metaclass PackageMerge."""
    __spec__ = SPECIFICATIONS['PackageMerge']
    mergedPackage: Package | None
    receivingPackage: Package | None
