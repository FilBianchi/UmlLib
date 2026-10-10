from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Constraint import Constraint

class InteractionConstraint(Constraint):
    """UML metaclass InteractionConstraint."""
    __spec__ = SPECIFICATIONS['InteractionConstraint']
    maxint: ValueSpecification | None
    minint: ValueSpecification | None
