from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._CallAction import CallAction

class CallOperationAction(CallAction):
    """UML metaclass CallOperationAction."""
    __spec__ = SPECIFICATIONS['CallOperationAction']
    operation: Operation | None
    target: InputPin | None
