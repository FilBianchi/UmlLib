from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._IntervalConstraint import IntervalConstraint

class TimeConstraint(IntervalConstraint):
    """UML metaclass TimeConstraint."""
    __spec__ = SPECIFICATIONS['TimeConstraint']
    firstEvent: bool | None
    specification: TimeInterval | None
