from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment

class OccurrenceSpecification(InteractionFragment):
    """UML metaclass OccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['OccurrenceSpecification']
    covered: Lifeline | None
    toAfter: list[GeneralOrdering]
    toBefore: list[GeneralOrdering]
