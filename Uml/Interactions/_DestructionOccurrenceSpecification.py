from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._MessageOccurrenceSpecification import MessageOccurrenceSpecification

class DestructionOccurrenceSpecification(MessageOccurrenceSpecification):
    """UML metaclass DestructionOccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['DestructionOccurrenceSpecification']
