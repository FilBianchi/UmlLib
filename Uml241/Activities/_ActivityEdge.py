from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._RedefinableElement import RedefinableElement

class ActivityEdge(RedefinableElement):
    """UML metaclass ActivityEdge."""
    __spec__ = SPECIFICATIONS['ActivityEdge']
    activity: Activity | None
    guard: ValueSpecification | None
    inGroup: list[ActivityGroup]
    inPartition: list[ActivityPartition]
    inStructuredNode: StructuredActivityNode | None
    interrupts: InterruptibleActivityRegion | None
    redefinedEdge: list[ActivityEdge]
    source: ActivityNode | None
    target: ActivityNode | None
    weight: ValueSpecification | None
