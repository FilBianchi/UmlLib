from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Packages._Package import Package

class Profile(Package):
    """UML metaclass Profile."""
    __spec__ = SPECIFICATIONS['Profile']
    metaclassReference: list[ElementImport]
    metamodelReference: list[PackageImport]
