from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._NamedElement import NamedElement

class InteractionFragment(NamedElement):
    """UML metaclass InteractionFragment."""
    __spec__ = SPECIFICATIONS['InteractionFragment']
    covered: list[Lifeline]
    enclosingInteraction: Interaction | None
    enclosingOperand: InteractionOperand | None
    generalOrdering: list[GeneralOrdering]
