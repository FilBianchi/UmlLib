from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._PackageableElement import PackageableElement

class Constraint(PackageableElement):
    """UML metaclass Constraint."""
    __spec__ = SPECIFICATIONS['Constraint']
    constrainedElement: list[Element]
    context: Namespace | None
    specification: ValueSpecification | None
