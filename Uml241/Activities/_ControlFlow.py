from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ActivityEdge import ActivityEdge

class ControlFlow(ActivityEdge):
    """UML metaclass ControlFlow."""
    __spec__ = SPECIFICATIONS['ControlFlow']
