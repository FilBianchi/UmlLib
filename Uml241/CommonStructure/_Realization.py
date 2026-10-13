from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Abstraction import Abstraction

class Realization(Abstraction):
    """UML metaclass Realization."""
    __spec__ = SPECIFICATIONS['Realization']
