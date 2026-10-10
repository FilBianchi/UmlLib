from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Packages._Package import Package

class Model(Package):
    """UML metaclass Model."""
    __spec__ = SPECIFICATIONS['Model']
    viewpoint: str | None
