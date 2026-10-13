from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..CommonStructure._Element import Element

class Image(Element):
    """UML metaclass Image."""
    __spec__ = SPECIFICATIONS['Image']
    content: str | None
    format: str | None
    location: str | None
