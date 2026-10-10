from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ActivityGroup import ActivityGroup

class InterruptibleActivityRegion(ActivityGroup):
    """UML metaclass InterruptibleActivityRegion."""
    __spec__ = SPECIFICATIONS['InterruptibleActivityRegion']
    interruptingEdge: list[ActivityEdge]
    node: list[ActivityNode]
