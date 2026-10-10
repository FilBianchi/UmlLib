from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class Relationship(Element):
    """UML metaclass Relationship."""
    __spec__ = SPECIFICATIONS['Relationship']
    relatedElement: list[Element]
