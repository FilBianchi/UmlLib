from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..Actions._LinkEndData import LinkEndData

class LinkEndCreationData(LinkEndData):
    """UML metaclass LinkEndCreationData."""
    __spec__ = SPECIFICATIONS['LinkEndCreationData']
    insertAt: InputPin | None
    isReplaceAll: bool | None
    def allPins(self, *args, **kwargs):
        try:
            return _operation(self, 'LinkEndCreationData', 'allPins', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
