from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._Interval import Interval

class TimeInterval(Interval):
    """UML metaclass TimeInterval."""
    __spec__ = SPECIFICATIONS['TimeInterval']
    max: TimeExpression | None
    min: TimeExpression | None
