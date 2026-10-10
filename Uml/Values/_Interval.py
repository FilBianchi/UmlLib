from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._ValueSpecification import ValueSpecification

class Interval(ValueSpecification):
    """UML metaclass Interval."""
    __spec__ = SPECIFICATIONS['Interval']
    max: ValueSpecification | None
    min: ValueSpecification | None
