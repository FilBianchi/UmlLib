from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class Comment(Element):
    """UML metaclass Comment."""
    __spec__ = SPECIFICATIONS['Comment']
    annotatedElement: list[Element]
    body: str | None
