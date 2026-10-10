from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._IntervalConstraint import IntervalConstraint

class TimeConstraint(IntervalConstraint):
    """UML metaclass TimeConstraint."""
    __spec__ = SPECIFICATIONS['TimeConstraint']
    firstEvent: bool | None
    specification: TimeInterval | None
