from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._OccurrenceSpecification import OccurrenceSpecification

class ExecutionOccurrenceSpecification(OccurrenceSpecification):
    """UML metaclass ExecutionOccurrenceSpecification."""
    __spec__ = SPECIFICATIONS['ExecutionOccurrenceSpecification']
    execution: ExecutionSpecification | None
