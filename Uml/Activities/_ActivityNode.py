from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
    def containingActivity(self, *args, **kwargs):
        try:
            return _operation(self, 'ActivityNode', 'containingActivity', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
    def isConsistentWith(self, *args, **kwargs):
        try:
            return _operation(self, 'ActivityNode', 'isConsistentWith', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
