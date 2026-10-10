from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class Comment(Element):
    """UML metaclass Comment."""
    __spec__ = SPECIFICATIONS['Comment']
    annotatedElement: list[Element]
    body: str | None
