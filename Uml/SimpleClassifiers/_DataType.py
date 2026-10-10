from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Classifier import Classifier

class DataType(Classifier):
    """UML metaclass DataType."""
    __spec__ = SPECIFICATIONS['DataType']
    ownedAttribute: list[Property]
    ownedOperation: list[Operation]
