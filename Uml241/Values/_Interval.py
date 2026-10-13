from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._ValueSpecification import ValueSpecification

class Interval(ValueSpecification):
    """UML metaclass Interval."""
    __spec__ = SPECIFICATIONS['Interval']
    max: ValueSpecification | None
    min: ValueSpecification | None
