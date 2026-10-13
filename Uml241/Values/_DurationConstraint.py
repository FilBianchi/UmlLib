from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._IntervalConstraint import IntervalConstraint

class DurationConstraint(IntervalConstraint):
    """UML metaclass DurationConstraint."""
    __spec__ = SPECIFICATIONS['DurationConstraint']
    firstEvent: list[bool]
    specification: DurationInterval | None
