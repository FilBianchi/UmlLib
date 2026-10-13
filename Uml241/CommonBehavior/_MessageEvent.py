from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonBehavior._Event import Event

class MessageEvent(Event):
    """UML metaclass MessageEvent."""
    __spec__ = SPECIFICATIONS['MessageEvent']
