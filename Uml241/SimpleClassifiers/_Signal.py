from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Classification._Classifier import Classifier

class Signal(Classifier):
    """UML metaclass Signal."""
    __spec__ = SPECIFICATIONS['Signal']
    ownedAttribute: list[Property]
