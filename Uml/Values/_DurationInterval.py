from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._Interval import Interval

class DurationInterval(Interval):
    """UML metaclass DurationInterval."""
    __spec__ = SPECIFICATIONS['DurationInterval']
    max: Duration | None
    min: Duration | None
