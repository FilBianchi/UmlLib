from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Packages._Package import Package

class Profile(Package):
    """UML metaclass Profile."""
    __spec__ = SPECIFICATIONS['Profile']
    metaclassReference: list[ElementImport]
    metamodelReference: list[PackageImport]
