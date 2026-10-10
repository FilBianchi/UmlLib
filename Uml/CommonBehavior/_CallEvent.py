from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonBehavior._MessageEvent import MessageEvent

class CallEvent(MessageEvent):
    """UML metaclass CallEvent."""
    __spec__ = SPECIFICATIONS['CallEvent']
    operation: Operation | None
