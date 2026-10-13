from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._InvocationAction import InvocationAction

class SendObjectAction(InvocationAction):
    """UML metaclass SendObjectAction."""
    __spec__ = SPECIFICATIONS['SendObjectAction']
    request: InputPin | None
    target: InputPin | None
