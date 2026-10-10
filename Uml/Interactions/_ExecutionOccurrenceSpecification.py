from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Interactions._OccurrenceSpecification import OccurrenceSpecification

class ExecutionOccurrenceSpecification(OccurrenceSpecification):
    """UML metaclass ExecutionOccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['ExecutionOccurrenceSpecification']
    execution: ExecutionSpecification | None
