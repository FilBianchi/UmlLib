from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment
from ..CommonStructure._Namespace import Namespace

class InteractionOperand(InteractionFragment, Namespace):
    """UML metaclass InteractionOperand."""
    __spec__ = SPECIFICATIONS['InteractionOperand']
    fragment: list[InteractionFragment]
    guard: InteractionConstraint | None
