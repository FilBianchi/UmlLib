from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._NamedElement import NamedElement

class InteractionFragment(NamedElement):
    """UML metaclass InteractionFragment."""
    __spec__ = SPECIFICATIONS['InteractionFragment']
    covered: list[Lifeline]
    enclosingInteraction: Interaction | None
    enclosingOperand: InteractionOperand | None
    generalOrdering: list[GeneralOrdering]
