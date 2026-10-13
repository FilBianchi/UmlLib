from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._RedefinableElement import RedefinableElement

class ActivityNode(RedefinableElement):
    """UML metaclass ActivityNode."""
    __spec__ = SPECIFICATIONS['ActivityNode']
    activity: Activity | None
    inGroup: list[ActivityGroup]
    inInterruptibleRegion: list[InterruptibleActivityRegion]
    inPartition: list[ActivityPartition]
    inStructuredNode: StructuredActivityNode | None
    incoming: list[ActivityEdge]
    outgoing: list[ActivityEdge]
    redefinedNode: list[ActivityNode]
