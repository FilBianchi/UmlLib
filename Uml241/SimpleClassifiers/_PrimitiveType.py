from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..SimpleClassifiers._DataType import DataType

class PrimitiveType(DataType):
    """UML metaclass PrimitiveType."""
    __spec__ = SPECIFICATIONS['PrimitiveType']
