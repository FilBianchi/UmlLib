from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class Slot(Element):
    """UML metaclass Slot."""
    __spec__ = SPECIFICATIONS['Slot']
    definingFeature: StructuralFeature | None
    owningInstance: InstanceSpecification | None
    value: list[ValueSpecification]
