from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._Interval import Interval

class DurationInterval(Interval):
    """UML metaclass DurationInterval."""
    __spec__ = SPECIFICATIONS['DurationInterval']
    max: Duration | None
    min: Duration | None
