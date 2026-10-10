from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._Interval import Interval

class TimeInterval(Interval):
    """UML metaclass TimeInterval."""
    __spec__ = SPECIFICATIONS['TimeInterval']
    max: TimeExpression | None
    min: TimeExpression | None
