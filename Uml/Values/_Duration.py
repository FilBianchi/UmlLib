from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Values._ValueSpecification import ValueSpecification

class Duration(ValueSpecification):
    """UML metaclass Duration."""
    __spec__ = SPECIFICATIONS['Duration']
    expr: ValueSpecification | None
    observation: list[Observation]
