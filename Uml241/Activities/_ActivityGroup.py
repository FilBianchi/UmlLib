from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class ActivityGroup(NamedElement):
    """UML metaclass ActivityGroup."""
    __spec__ = SPECIFICATIONS['ActivityGroup']
    containedEdge: list[ActivityEdge]
    containedNode: list[ActivityNode]
    inActivity: Activity | None
    subgroup: list[ActivityGroup]
    superGroup: ActivityGroup | None
