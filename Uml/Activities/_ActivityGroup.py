from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class ActivityGroup(NamedElement):
    """UML metaclass ActivityGroup."""
    __spec__ = SPECIFICATIONS['ActivityGroup']
    containedEdge: list[ActivityEdge]
    containedNode: list[ActivityNode]
    inActivity: Activity | None
    subgroup: list[ActivityGroup]
    superGroup: ActivityGroup | None
    def containingActivity(self, *args, **kwargs):
        try:
            return _operation(self, 'ActivityGroup', 'containingActivity', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
