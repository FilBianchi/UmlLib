from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._LinkEndData import LinkEndData

class LinkEndCreationData(LinkEndData):
    """UML metaclass LinkEndCreationData."""
    __spec__ = SPECIFICATIONS['LinkEndCreationData']
    insertAt: InputPin | None
    isReplaceAll: bool | None
