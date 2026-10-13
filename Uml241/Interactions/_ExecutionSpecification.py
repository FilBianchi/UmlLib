from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Interactions._InteractionFragment import InteractionFragment

class ExecutionSpecification(InteractionFragment):
    """UML metaclass ExecutionSpecification."""
    __spec__ = SPECIFICATIONS['ExecutionSpecification']
    finish: OccurrenceSpecification | None
    start: OccurrenceSpecification | None
