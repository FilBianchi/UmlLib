from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class LinkEndData(Element):
    """UML metaclass LinkEndData."""
    __spec__ = SPECIFICATIONS['LinkEndData']
    end: Property | None
    qualifier: list[QualifierValue]
    value: InputPin | None
