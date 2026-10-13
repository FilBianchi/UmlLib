from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Packages._Package import Package

class Model(Package):
    """UML metaclass Model."""
    __spec__ = SPECIFICATIONS['Model']
    viewpoint: str | None
