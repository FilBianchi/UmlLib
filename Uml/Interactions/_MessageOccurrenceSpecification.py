from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._MessageEnd import MessageEnd
from ..Interactions._OccurrenceSpecification import OccurrenceSpecification

class MessageOccurrenceSpecification(MessageEnd, OccurrenceSpecification):
    """UML metaclass MessageOccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['MessageOccurrenceSpecification']
