from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonBehavior._MessageEvent import MessageEvent

class AnyReceiveEvent(MessageEvent):
    """UML metaclass AnyReceiveEvent."""
    __spec__ = SPECIFICATIONS['AnyReceiveEvent']
