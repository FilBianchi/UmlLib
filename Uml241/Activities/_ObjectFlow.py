from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Activities._ActivityEdge import ActivityEdge

class ObjectFlow(ActivityEdge):
    """UML metaclass ObjectFlow."""
    __spec__ = SPECIFICATIONS['ObjectFlow']
    isMulticast: bool | None
    isMultireceive: bool | None
    selection: Behavior | None
    transformation: Behavior | None
