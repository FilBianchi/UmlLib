from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Values._ValueSpecification import ValueSpecification

class TimeExpression(ValueSpecification):
    """UML metaclass TimeExpression."""
    __spec__ = SPECIFICATIONS['TimeExpression']
    expr: ValueSpecification | None
    observation: list[Observation]
