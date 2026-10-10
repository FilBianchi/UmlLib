from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Classification._Classifier import Classifier

class Signal(Classifier):
    """UML metaclass Signal."""
    __spec__ = SPECIFICATIONS['Signal']
    ownedAttribute: list[Property]
