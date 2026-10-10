from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'ActivityEdge', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
