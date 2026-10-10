from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Abstraction import Abstraction

class Realization(Abstraction):
    """UML metaclass Realization."""
    __spec__ = SPECIFICATIONS['Realization']
