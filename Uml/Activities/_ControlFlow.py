from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ActivityEdge import ActivityEdge

class ControlFlow(ActivityEdge):
    """UML metaclass ControlFlow."""
    __spec__ = SPECIFICATIONS['ControlFlow']
