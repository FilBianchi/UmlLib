from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Dependency import Dependency

class Abstraction(Dependency):
    """UML metaclass Abstraction."""
    __spec__ = SPECIFICATIONS['Abstraction']
    mapping: OpaqueExpression | None
