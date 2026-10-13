from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ActivityGroup import ActivityGroup

class ActivityPartition(ActivityGroup):
    """UML metaclass ActivityPartition."""
    __spec__ = SPECIFICATIONS['ActivityPartition']
    edge: list[ActivityEdge]
    isDimension: bool | None
    isExternal: bool | None
    node: list[ActivityNode]
    represents: Element | None
    subpartition: list[ActivityPartition]
    superPartition: ActivityPartition | None
