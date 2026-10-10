from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class Image(Element):
    """UML metaclass Image."""
    __spec__ = SPECIFICATIONS['Image']
    content: str | None
    format: str | None
    location: str | None
