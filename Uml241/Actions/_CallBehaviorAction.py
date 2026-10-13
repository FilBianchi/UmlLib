from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._CallAction import CallAction

class CallBehaviorAction(CallAction):
    """UML metaclass CallBehaviorAction."""
    __spec__ = SPECIFICATIONS['CallBehaviorAction']
    behavior: Behavior | None
