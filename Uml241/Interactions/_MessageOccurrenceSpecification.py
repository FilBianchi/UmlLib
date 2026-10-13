from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._MessageEnd import MessageEnd
from ..Interactions._OccurrenceSpecification import OccurrenceSpecification

class MessageOccurrenceSpecification(MessageEnd, OccurrenceSpecification):
    """UML metaclass MessageOccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['MessageOccurrenceSpecification']
