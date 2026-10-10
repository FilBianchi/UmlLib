from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._InteractionFragment import InteractionFragment

class OccurrenceSpecification(InteractionFragment):
    """UML metaclass OccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['OccurrenceSpecification']
    covered: Lifeline | None
    toAfter: list[GeneralOrdering]
    toBefore: list[GeneralOrdering]
