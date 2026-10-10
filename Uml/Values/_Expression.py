from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._ValueSpecification import ValueSpecification

class Expression(ValueSpecification):
    """UML metaclass Expression."""
    __spec__ = SPECIFICATIONS['Expression']
    operand: list[ValueSpecification]
    symbol: str | None
