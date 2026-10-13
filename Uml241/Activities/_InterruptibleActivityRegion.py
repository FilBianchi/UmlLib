from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ActivityGroup import ActivityGroup

class InterruptibleActivityRegion(ActivityGroup):
    """UML metaclass InterruptibleActivityRegion."""
    __spec__ = SPECIFICATIONS['InterruptibleActivityRegion']
    interruptingEdge: list[ActivityEdge]
    node: list[ActivityNode]
