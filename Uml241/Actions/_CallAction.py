from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._InvocationAction import InvocationAction

class CallAction(InvocationAction):
    """UML metaclass CallAction."""
    __spec__ = SPECIFICATIONS['CallAction']
    isSynchronous: bool | None
    result: list[OutputPin]
