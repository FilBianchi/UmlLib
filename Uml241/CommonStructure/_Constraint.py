from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._PackageableElement import PackageableElement

class Constraint(PackageableElement):
    """UML metaclass Constraint."""
    __spec__ = SPECIFICATIONS['Constraint']
    constrainedElement: list[Element]
    context: Namespace | None
    specification: ValueSpecification | None
