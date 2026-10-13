from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class Slot(Element):
    """UML metaclass Slot."""
    __spec__ = SPECIFICATIONS['Slot']
    definingFeature: StructuralFeature | None
    owningInstance: InstanceSpecification | None
    value: list[ValueSpecification]
