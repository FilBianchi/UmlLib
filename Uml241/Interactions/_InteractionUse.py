from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment

class InteractionUse(InteractionFragment):
    """UML metaclass InteractionUse."""
    __spec__ = SPECIFICATIONS['InteractionUse']
    actualGate: list[Gate]
    argument: list[ValueSpecification]
    refersTo: Interaction | None
    returnValue: ValueSpecification | None
    returnValueRecipient: Property | None
