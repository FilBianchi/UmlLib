from __future__ import annotations
from enum import Enum
from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError
from umltools.semantics import operation as _operation
from umltools.native import NativeNotImplemented
from ..CommonStructure._Element import Element

class LinkEndData(Element):
    """UML metaclass LinkEndData."""
    __spec__ = SPECIFICATIONS['LinkEndData']
    end: Property | None
    qualifier: list[QualifierValue]
    value: InputPin | None
    def allPins(self, *args, **kwargs):
        try:
            return _operation(self, 'LinkEndData', 'allPins', args, kwargs)
        except NativeNotImplemented as error:
            raise UnsupportedSemanticsError(str(error)) from error
