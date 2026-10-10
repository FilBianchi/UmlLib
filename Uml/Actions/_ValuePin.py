from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._InputPin import InputPin

class ValuePin(InputPin):
    """UML metaclass ValuePin."""
    __spec__ = SPECIFICATIONS['ValuePin']
    value: ValueSpecification | None
