from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
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
