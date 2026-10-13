from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._MessageOccurrenceSpecification import MessageOccurrenceSpecification

class DestructionOccurrenceSpecification(MessageOccurrenceSpecification):
    """UML metaclass DestructionOccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['DestructionOccurrenceSpecification']
