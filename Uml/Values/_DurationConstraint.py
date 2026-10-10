from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._IntervalConstraint import IntervalConstraint

class DurationConstraint(IntervalConstraint):
    """UML metaclass DurationConstraint."""
    __spec__ = SPECIFICATIONS['DurationConstraint']
    firstEvent: list[bool]
    specification: DurationInterval | None
