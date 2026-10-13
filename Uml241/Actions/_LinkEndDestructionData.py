from __future__ import annotations
from enum import Enum
from Uml241._runtime import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError, NativeNotImplemented
from Uml241._runtime import operation as _operation
from ..Actions._LinkEndData import LinkEndData

class LinkEndDestructionData(LinkEndData):
    """UML metaclass LinkEndDestructionData."""
    __spec__ = SPECIFICATIONS['LinkEndDestructionData']
    destroyAt: InputPin | None
    isDestroyDuplicates: bool | None
