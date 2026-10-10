from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..SimpleClassifiers._DataType import DataType

class Enumeration(DataType):
    """UML metaclass Enumeration."""
    __spec__ = SPECIFICATIONS['Enumeration']
    ownedLiteral: list[EnumerationLiteral]
