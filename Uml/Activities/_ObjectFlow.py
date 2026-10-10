from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ActivityEdge import ActivityEdge

class ObjectFlow(ActivityEdge):
    """UML metaclass ObjectFlow."""
    __spec__ = SPECIFICATIONS['ObjectFlow']
    isMulticast: bool | None
    isMultireceive: bool | None
    selection: Behavior | None
    transformation: Behavior | None
