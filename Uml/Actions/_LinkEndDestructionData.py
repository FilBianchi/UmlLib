from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._LinkEndData import LinkEndData

class LinkEndDestructionData(LinkEndData):
    """UML metaclass LinkEndDestructionData."""
    __spec__ = SPECIFICATIONS['LinkEndDestructionData']
    destroyAt: InputPin | None
    isDestroyDuplicates: bool | None
    def allPins(self, *args, **kwargs):
        try:
            return _operation(self, 'LinkEndDestructionData', 'allPins', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
