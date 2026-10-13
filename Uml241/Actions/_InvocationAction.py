from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._Action import Action

class InvocationAction(Action):
    """UML metaclass InvocationAction."""
    __spec__ = SPECIFICATIONS['InvocationAction']
    argument: list[InputPin]
    onPort: Port | None
