from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonBehavior._MessageEvent import MessageEvent

class SignalEvent(MessageEvent):
    """UML metaclass SignalEvent."""
    __spec__ = SPECIFICATIONS['SignalEvent']
    signal: Signal | None
