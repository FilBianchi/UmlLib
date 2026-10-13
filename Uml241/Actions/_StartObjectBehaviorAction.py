from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._CallAction import CallAction

class StartObjectBehaviorAction(CallAction):
    """UML metaclass StartObjectBehaviorAction."""
    __spec__ = SPECIFICATIONS['StartObjectBehaviorAction']
    object: InputPin | None
