from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Constraint import Constraint

class IntervalConstraint(Constraint):
    """UML metaclass IntervalConstraint."""
    __spec__ = SPECIFICATIONS['IntervalConstraint']
    specification: Interval | None
