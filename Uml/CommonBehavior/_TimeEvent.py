from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonBehavior._Event import Event

class TimeEvent(Event):
    """UML metaclass TimeEvent."""
    __spec__ = SPECIFICATIONS['TimeEvent']
    isRelative: bool | None
    when: TimeExpression | None
