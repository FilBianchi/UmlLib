from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Constraint import Constraint

class InteractionConstraint(Constraint):
    """UML metaclass InteractionConstraint."""
    __spec__ = SPECIFICATIONS['InteractionConstraint']
    maxint: ValueSpecification | None
    minint: ValueSpecification | None
