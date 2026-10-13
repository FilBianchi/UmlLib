from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class Relationship(Element):
    """UML metaclass Relationship."""
    __spec__ = SPECIFICATIONS['Relationship']
    relatedElement: list[Element]
