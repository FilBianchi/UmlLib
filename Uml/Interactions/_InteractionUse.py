from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionFragment import InteractionFragment

class InteractionUse(InteractionFragment):
    """UML metaclass InteractionUse."""
    __spec__ = SPECIFICATIONS['InteractionUse']
    actualGate: list[Gate]
    argument: list[ValueSpecification]
    refersTo: Interaction | None
    returnValue: ValueSpecification | None
    returnValueRecipient: Property | None
