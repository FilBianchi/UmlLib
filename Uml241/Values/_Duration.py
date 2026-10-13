from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._ValueSpecification import ValueSpecification

class Duration(ValueSpecification):
    """UML metaclass Duration."""
    __spec__ = SPECIFICATIONS['Duration']
    expr: ValueSpecification | None
    observation: list[Observation]
