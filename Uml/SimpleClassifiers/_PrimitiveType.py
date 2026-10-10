from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..SimpleClassifiers._DataType import DataType

class PrimitiveType(DataType):
    """UML metaclass PrimitiveType."""
    __spec__ = SPECIFICATIONS['PrimitiveType']
