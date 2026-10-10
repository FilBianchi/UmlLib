from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Activities._ActivityNode import ActivityNode

class ExecutableNode(ActivityNode):
    """UML metaclass ExecutableNode."""
    __spec__ = SPECIFICATIONS['ExecutableNode']
    handler: list[ExceptionHandler]
